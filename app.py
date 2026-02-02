import os
import json
import base64
import random
from datetime import datetime, date
from io import BytesIO

import streamlit as st
import yaml
import pandas as pd
import altair as alt
from pypdf import PdfReader

from openai import OpenAI
import google.generativeai as genai
from anthropic import Anthropic
import httpx

# =========================
# Models / Providers
# =========================

ALL_MODELS = [
    # OpenAI
    "gpt-4o-mini",
    "gpt-4.1-mini",
    # Gemini
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
    "gemini-2.5-flash-lite",
    "gemini-3-pro-preview",
    # Anthropic (expandable)
    "claude-3-5-sonnet-2024-10",
    "claude-3-5-haiku-20241022",
    # Grok
    "grok-4-fast-reasoning",
    "grok-3-mini",
]

OPENAI_MODELS = {"gpt-4o-mini", "gpt-4.1-mini"}
GEMINI_MODELS = {
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
    "gemini-2.5-flash-lite",
    "gemini-3-pro-preview",
}
ANTHROPIC_MODELS = {
    "claude-3-5-sonnet-2024-10",
    "claude-3-5-haiku-20241022",
}
GROK_MODELS = {"grok-4-fast-reasoning", "grok-3-mini"}

# =========================
# Painter styles (WOW)
# =========================

PAINTER_STYLES = [
    "Van Gogh", "Monet", "Picasso", "Da Vinci", "Rembrandt",
    "Matisse", "Kandinsky", "Hokusai", "Yayoi Kusama", "Frida Kahlo",
    "Salvador Dali", "Rothko", "Pollock", "Chagall", "Basquiat",
    "Haring", "Georgia O'Keeffe", "Turner", "Seurat", "Escher",
]

STYLE_CSS = {
    "Van Gogh": "body { background: radial-gradient(circle at top left, #243B55, #141E30); }",
    "Monet": "body { background: linear-gradient(120deg, #a1c4fd, #c2e9fb); }",
    "Picasso": "body { background: linear-gradient(135deg, #ff9a9e, #fecfef); }",
    "Da Vinci": "body { background: radial-gradient(circle, #f9f1c6, #c9a66b); }",
    "Rembrandt": "body { background: radial-gradient(circle, #2c1810, #0b090a); }",
    "Matisse": "body { background: linear-gradient(135deg, #ffecd2, #fcb69f); }",
    "Kandinsky": "body { background: linear-gradient(135deg, #00c6ff, #0072ff); }",
    "Hokusai": "body { background: linear-gradient(135deg, #2b5876, #4e4376); }",
    "Yayoi Kusama": "body { background: radial-gradient(circle, #ffdd00, #ff6a00); }",
    "Frida Kahlo": "body { background: linear-gradient(135deg, #f8b195, #f67280, #c06c84); }",
    "Salvador Dali": "body { background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d); }",
    "Rothko": "body { background: linear-gradient(135deg, #141E30, #243B55); }",
    "Pollock": "body { background: repeating-linear-gradient(45deg,#222,#222 10px,#333 10px,#333 20px); }",
    "Chagall": "body { background: linear-gradient(135deg, #a18cd1, #fbc2eb); }",
    "Basquiat": "body { background: linear-gradient(135deg, #f7971e, #ffd200); }",
    "Haring": "body { background: linear-gradient(135deg, #ff512f, #dd2476); }",
    "Georgia O'Keeffe": "body { background: linear-gradient(135deg, #ffefba, #ffffff); }",
    "Turner": "body { background: linear-gradient(135deg, #f8ffae, #43c6ac); }",
    "Seurat": "body { background: radial-gradient(circle, #e0eafc, #cfdef3); }",
    "Escher": "body { background: linear-gradient(135deg, #232526, #414345); }",
}

# =========================
# Localization
# =========================

LABELS = {
    "Dashboard": {"English": "Dashboard", "繁體中文": "儀表板"},
    "TW Premarket": {"English": "TW Premarket Application", "繁體中文": "第二、三等級醫療器材查驗登記"},
    "510k_tab": {"English": "510(k) Intelligence", "繁體中文": "510(k) 智能分析"},
    "PDF → Markdown": {"English": "PDF → Markdown", "繁體中文": "PDF → Markdown"},
    "Checklist & Report": {"English": "510(k) Review Pipeline", "繁體中文": "510(k) 審查全流程"},
    "Note Keeper & Magics": {"English": "Note Keeper & Magics", "繁體中文": "筆記助手與魔法"},
    "Agents Config": {"English": "Agents Config Studio", "繁體中文": "代理設定工作室"},
}

def t(key: str) -> str:
    lang = st.session_state.settings.get("language", "繁體中文")
    return LABELS.get(key, {}).get(lang, key)

# =========================
# CSS
# =========================

def apply_style(theme: str, painter_style: str):
    css = STYLE_CSS.get(painter_style, "")
    if theme == "Dark":
        css += """
        body { color: #e5e7eb; }
        .stButton>button { background-color: #111827; color: #fff; border-radius: 999px; }
        .stTextInput input, .stTextArea textarea { background:#0b1220; color:#e5e7eb; border-radius:12px; }
        .stSelectbox div[data-baseweb="select"] > div { background:#0b1220; color:#e5e7eb; border-radius:12px; }
        """
    else:
        css += """
        body { color: #111827; }
        .stButton>button { background-color: #2563eb; color: #fff; border-radius: 999px; }
        .stTextInput input, .stTextArea textarea { background:#ffffff; color:#111827; border-radius:12px; }
        .stSelectbox div[data-baseweb="select"] > div { background:#ffffff; color:#111827; border-radius:12px; }
        """
    css += """
    .wow-card{
      border-radius:18px;padding:14px 18px;margin-bottom:0.75rem;
      box-shadow:0 14px 35px rgba(15,23,42,0.35);
      border:1px solid rgba(148,163,184,0.35);
      backdrop-filter: blur(10px);
    }
    .wow-card-title{font-size:0.82rem;text-transform:uppercase;letter-spacing:0.12em;opacity:0.85}
    .wow-card-main{font-size:1.55rem;font-weight:800;margin-top:4px}
    .wow-badge{
      display:inline-flex;align-items:center;padding:2px 10px;border-radius:999px;
      font-size:0.75rem;font-weight:700;background:rgba(15,23,42,0.12);
      border:1px solid rgba(148,163,184,0.6)
    }
    .coral{ color: coral; font-weight: 700; }
    """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# =========================
# LLM Gateway
# =========================

def get_provider(model: str) -> str:
    if model in OPENAI_MODELS: return "openai"
    if model in GEMINI_MODELS: return "gemini"
    if model in ANTHROPIC_MODELS: return "anthropic"
    if model in GROK_MODELS: return "grok"
    raise ValueError(f"Unknown model: {model}")

def call_llm(
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 12000,
    temperature: float = 0.2,
    api_keys: dict | None = None,
) -> str:
    provider = get_provider(model)
    api_keys = api_keys or {}

    def get_key(name: str, env_var: str) -> str:
        return api_keys.get(name) or os.getenv(env_var) or ""

    if provider == "openai":
        key = get_key("openai", "OPENAI_API_KEY")
        if not key:
            raise RuntimeError("Missing OpenAI API key.")
        client = OpenAI(api_key=key)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role":"system","content":system_prompt},
                      {"role":"user","content":user_prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content

    if provider == "gemini":
        key = get_key("gemini", "GEMINI_API_KEY")
        if not key:
            raise RuntimeError("Missing Gemini API key.")
        genai.configure(api_key=key)
        llm = genai.GenerativeModel(model)
        resp = llm.generate_content(
            system_prompt + "\n\n" + user_prompt,
            generation_config={"max_output_tokens": max_tokens, "temperature": temperature},
        )
        return resp.text

    if provider == "anthropic":
        key = get_key("anthropic", "ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("Missing Anthropic API key.")
        client = Anthropic(api_key=key)
        resp = client.messages.create(
            model=model,
            system=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role":"user","content":user_prompt}],
        )
        return resp.content[0].text

    if provider == "grok":
        key = get_key("grok", "GROK_API_KEY")
        if not key:
            raise RuntimeError("Missing Grok (xAI) API key.")
        with httpx.Client(base_url="https://api.x.ai/v1", timeout=90) as client:
            resp = client.post(
                "/chat/completions",
                headers={"Authorization": f"Bearer {key}"},
                json={
                    "model": model,
                    "messages": [{"role":"system","content":system_prompt},
                                 {"role":"user","content":user_prompt}],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    raise RuntimeError(f"Unsupported provider for model {model}")

# =========================
# Helpers
# =========================

def show_status(step_name: str, status: str):
    color = {"pending":"gray","running":"#f59e0b","done":"#10b981","error":"#ef4444"}.get(status,"gray")
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;margin-bottom:0.25rem;">
          <div style="width:10px;height:10px;border-radius:50%;background:{color};margin-right:6px;"></div>
          <span style="font-size:0.92rem;">{step_name} – <b>{status}</b></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

def log_event(tab: str, agent: str, model: str, tokens_est: int):
    st.session_state["history"].append({
        "tab": tab, "agent": agent, "model": model,
        "tokens_est": tokens_est, "ts": datetime.utcnow().isoformat()
    })

def extract_pdf_pages_to_text(file, start_page: int, end_page: int) -> str:
    reader = PdfReader(file)
    n = len(reader.pages)
    start = max(0, start_page - 1)
    end = min(n, end_page)
    texts = []
    for i in range(start, end):
        try:
            texts.append(reader.pages[i].extract_text() or "")
        except Exception:
            texts.append("")
    return "\n\n".join(texts)

def highlight_keywords_simple(text: str, keywords: list[str], color: str = "coral") -> str:
    if not text: return text
    out = text
    for kw in sorted(set([k.strip() for k in keywords if k.strip()]), key=len, reverse=True):
        out = out.replace(kw, f'<span style="color:{color};font-weight:700;">{kw}</span>')
    return out

# =========================
# Unified Agent Runner UI
# =========================

def agent_run_ui(
    agent_id: str,
    tab_key: str,
    default_prompt: str,
    default_input_text: str = "",
    allow_model_override: bool = True,
    tab_label_for_history: str | None = None,
):
    agents_cfg = st.session_state.get("agents_cfg", {})
    agents_dict = agents_cfg.get("agents", {})
    agent_cfg = agents_dict.get(agent_id, {
        "name": agent_id,
        "model": st.session_state.settings["model"],
        "system_prompt": "",
        "max_tokens": st.session_state.settings["max_tokens"],
        "temperature": st.session_state.settings["temperature"],
    })

    status_key = f"{tab_key}_status"
    if status_key not in st.session_state:
        st.session_state[status_key] = "pending"

    show_status(agent_cfg.get("name", agent_id), st.session_state[status_key])

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        user_prompt = st.text_area(
            "Prompt（可修改）",
            value=st.session_state.get(f"{tab_key}_prompt", default_prompt),
            height=160, key=f"{tab_key}_prompt",
        )
    with col2:
        base_model = agent_cfg.get("model", st.session_state.settings["model"])
        model_index = ALL_MODELS.index(base_model) if base_model in ALL_MODELS else 0
        model = st.selectbox(
            "Model（可選）", ALL_MODELS,
            index=model_index, disabled=not allow_model_override, key=f"{tab_key}_model"
        )
    with col3:
        max_tokens = st.number_input(
            "max_tokens（可修改）", min_value=1000, max_value=120000,
            value=int(agent_cfg.get("max_tokens", st.session_state.settings["max_tokens"])),
            step=1000, key=f"{tab_key}_max_tokens",
        )

    input_text = st.text_area(
        "Input（可修改）",
        value=st.session_state.get(f"{tab_key}_input", default_input_text),
        height=260, key=f"{tab_key}_input",
    )

    colr1, colr2 = st.columns([1, 1])
    with colr1:
        run = st.button("Run Agent", key=f"{tab_key}_run")
    with colr2:
        use_output_as_next = st.button("Use edited output as NEXT input", key=f"{tab_key}_use_next")

    if run:
        st.session_state[status_key] = "running"
        show_status(agent_cfg.get("name", agent_id), "running")
        api_keys = st.session_state.get("api_keys", {})
        system_prompt = agent_cfg.get("system_prompt", "")
        user_full = f"{user_prompt}\n\n---\n\n{input_text}"

        with st.spinner("Running agent..."):
            try:
                out = call_llm(
                    model=model,
                    system_prompt=system_prompt,
                    user_prompt=user_full,
                    max_tokens=max_tokens,
                    temperature=st.session_state.settings["temperature"],
                    api_keys=api_keys,
                )
                st.session_state[f"{tab_key}_output"] = out
                st.session_state[status_key] = "done"
                token_est = int(len(user_full + out) / 4)
                log_event(tab_label_for_history or tab_key, agent_cfg.get("name", agent_id), model, token_est)
            except Exception as e:
                st.session_state[status_key] = "error"
                st.error(f"Agent error: {e}")

    output = st.session_state.get(f"{tab_key}_output", "")
    view_mode = st.radio("Output view", ["Markdown", "Plain text"], horizontal=True, key=f"{tab_key}_viewmode")
    edited = st.text_area(
        "Output（可編輯，將作為下一步輸入）",
        value=output,
        height=320,
        key=f"{tab_key}_output_edited",
    )

    if use_output_as_next:
        st.session_state[f"{tab_key}_next_input"] = edited
        st.success("已將編輯後輸出保存為 NEXT input（可在下一個 agent 的 input 直接貼上/套用）。")

# =========================
# TFDA Data Model Helpers
# =========================

MAIN_CATEGORIES = [
    "", "A.臨床化學及臨床毒理學", "B.血液學及病理學", "C.免疫學及微生物學",
    "D.麻醉學", "E.心臟血管醫學", "F.牙科學", "G.耳鼻喉科學",
    "H.胃腸病科學及泌尿科學", "I.一般及整形外科手術", "J.一般醫院及個人使用裝置",
    "K.神經科學", "L.婦產科學", "M.眼科學", "N.骨科學",
    "O.物理醫學科學", "P.放射學科學",
]

DEFAULT_CHANGE_ROWS = [
    "中文品名", "英文品名", "原廠標籤、說明書或包裝",
    "成分、材料、結構、規格或型號變更（未涉及安全及效能評估之尺寸規格變更）",
    "成分、材料、結構、規格或型號變更（涉及安全及效能評估）",
    "成分、材料、結構、規格或型號變更（新增規格、型號）",
    "成分、材料、結構、規格或型號變更（註銷規格、型號）",
    "效能、用途或適應症變更（含新增）",
    "變更製造業者名稱", "變更製造業者地址或製造國別", "變更製造業者地址（因門牌整編）",
    "變更許可證所有人（許可證讓與）", "變更許可證所有人名稱",
    "遺失補發或汙損換發（許可證）", "遺失補發或汙損換發（說明書）",
    "製造許可編號", "其它（非上述變更類型）",
]

DEFAULT_ATTACHMENTS = [
    ("1", "一、醫療器材許可證變更登記申請書"),
    ("2", "二、原核准文件（原許可證/騎縫章標籤、說明書或包裝）"),
    ("4", "四、變更說明文件（比較表/原廠變更說明函）"),
    ("5", "五、經本部核准類似品或相關產品資料"),
    ("6", "六、醫療器材商許可執照影本"),
    ("7", "七、出產國製售證明"),
    ("8", "八、國外原廠授權登記書"),
    ("9", "九、QMS/QSD 證明文件"),
    ("10", "十、委託製造相關文件"),
    ("11", "十一、標籤、說明書或包裝擬稿"),
    ("12", "十二、產品之結構、材料、規格、性能、用途、圖樣等資料"),
    ("14", "十四、產品特定安全性要求"),
    ("15", "十五、EP/STED 摘要（如適用）"),
    ("16", "十六、替代臨床前/品管資料之文件"),
    ("17", "十七、臨床前測試及原廠品質管制資料"),
    ("18", "十八、臨床證據資料"),
]

def init_tw_application_if_missing():
    if "tw_application" in st.session_state:
        return
    st.session_state["tw_application"] = {
        "basic_data": {
            "fill_date": "",
            "received_date": "",
            "device_type": "一般醫材",
            "case_category": "新案",
            "case_type": "許可證變更",
            "license_scope": "許可證號",
            "license_number": "",
            "device_name_zh": "",
            "device_name_en": "",
            "risk_class": "第二等級",
            "origin": "國產",
            "has_similar_products": "有",
            "substitution": "否",
            "change_reason": "",
        },
        "classifications": [
            {"main_category": "A.臨床化學及臨床毒理學", "sub_category_code": "A.1345", "sub_category_name": "葡萄糖試驗系統"}
        ],
        "change_items": [{"change_item": x, "original_approval": "", "requested_change": ""} for x in DEFAULT_CHANGE_ROWS],
        "applicant": {
            "company_uniform_no": "",
            "company_name": "",
            "company_address": "",
            "responsible_person": "",
            "contact_person": "",
            "contact_phone": "",
            "contact_email": "",
            "previous_values": {
                "company_uniform_no": "",
                "company_name": "",
                "company_address": "",
                "responsible_person": "",
            }
        },
        "attachments": [
            {"section_id": sid, "section_title": title, "applicability": "未判定", "notes": "", "files": []}
            for sid, title in DEFAULT_ATTACHMENTS
        ],
    }

def tw_completeness_score(app: dict) -> tuple[float, list[str]]:
    missing = []
    bd = app.get("basic_data", {})
    applicant = app.get("applicant", {})
    classifications = app.get("classifications", [])

    def req(cond, label):
        if not cond: missing.append(label)

    # basic required
    req(bool(bd.get("fill_date")), "填表日")
    req(bool(bd.get("received_date")), "公文收文日")
    req(bool(bd.get("device_type")), "醫療器材類型")
    req(bool(bd.get("case_category")), "案件種類")
    req(bool(bd.get("case_type")), "案件類型")
    req(bool(bd.get("device_name_zh","").strip()), "中文名稱")
    req(bool(bd.get("device_name_en","").strip()), "英文名稱")
    req(bool(bd.get("risk_class")), "風險等級")
    req(bool(bd.get("origin")), "產地")

    if bd.get("license_scope") == "許可證號":
        req(bool(bd.get("license_number","").strip()), "許可證號")

    req(isinstance(classifications, list) and len(classifications) >= 1, "至少一筆類別（主分類/次分類）")

    # applicant required
    req(bool(applicant.get("company_uniform_no","").strip()), "統一編號")
    req(bool(applicant.get("company_name","").strip()), "醫療器材商名稱")
    req(bool(applicant.get("company_address","").strip()), "地址")
    req(bool(applicant.get("responsible_person","").strip()), "負責人姓名")
    req(bool(applicant.get("contact_person","").strip()), "聯絡人姓名")
    req(bool(applicant.get("contact_phone","").strip()), "電話")
    req(bool(applicant.get("contact_email","").strip()), "電子郵件")

    # reason required for change
    if bd.get("case_type") == "許可證變更":
        req(bool(bd.get("change_reason","").strip()), "說明理由（許可證變更必填）")

    # weighted scoring (simple)
    total_required = 1 if False else 1  # placeholder to avoid lint
    total_required = len(missing) + 1  # not used directly

    # score as filled ratio among a fixed list
    fixed_list = [
        "填表日","公文收文日","醫療器材類型","案件種類","案件類型","中文名稱","英文名稱","風險等級","產地",
        "許可證號","至少一筆類別（主分類/次分類）","統一編號","醫療器材商名稱","地址","負責人姓名","聯絡人姓名","電話","電子郵件","說明理由（許可證變更必填）"
    ]
    # determine which are applicable
    applicable = []
    for k in fixed_list:
        if k == "許可證號" and bd.get("license_scope") != "許可證號":
            continue
        if k == "說明理由（許可證變更必填）" and bd.get("case_type") != "許可證變更":
            continue
        applicable.append(k)

    score = (len(applicable) - len([m for m in missing if m in applicable])) / max(1, len(applicable))
    return score, missing

def render_tw_application_markdown(app: dict) -> str:
    bd = app["basic_data"]
    cls = app.get("classifications", [])
    chg = app.get("change_items", [])
    ap = app.get("applicant", {})
    atts = app.get("attachments", [])

    # classification table
    cls_rows = []
    for i, r in enumerate(cls, start=1):
        cls_rows.append(f"| {i:02d} | {r.get('main_category','')} | {r.get('sub_category_code','')} | {r.get('sub_category_name','')} |")
    cls_table = "\n".join([
        "| ID | 主分類 | 次分類代碼 | 次分類名稱 |",
        "|---:|---|---|---|",
        *cls_rows
    ]) if cls_rows else "_（尚未填寫分類分級品項）_"

    # change table
    chg_rows = []
    for r in chg:
        chg_rows.append(f"| {r.get('change_item','')} | {r.get('original_approval','')} | {r.get('requested_change','')} |")
    chg_table = "\n".join([
        "| 變更項目 | 原核准登記事項 | 申請變更事項 |",
        "|---|---|---|",
        *chg_rows
    ]) if chg_rows else "_（尚未填寫變更內容）_"

    # attachments table
    att_rows = []
    for r in atts:
        files = r.get("files", [])
        if files:
            ftxt = "<br>".join([f"- {f.get('file_name','')}（{f.get('status','')}）" for f in files])
        else:
            ftxt = "（無）"
        att_rows.append(f"| {r.get('section_id','')} | {r.get('section_title','')} | {r.get('applicability','')} | {r.get('notes','')} | {ftxt} |")
    att_table = "\n".join([
        "| 節次 | 文件/附件 | 勾選 | 備註 | 檔案列 |",
        "|---:|---|---|---|---|",
        *att_rows
    ])

    prev = ap.get("previous_values", {})
    prev_block = ""
    if any((prev.get("company_uniform_no","").strip(), prev.get("company_name","").strip(),
            prev.get("company_address","").strip(), prev.get("responsible_person","").strip())):
        prev_block = f"""
### 修正前（如適用）
- 統一編號：{prev.get("company_uniform_no","")}
- 醫療器材商名稱：{prev.get("company_name","")}
- 地址：{prev.get("company_address","")}
- 負責人姓名：{prev.get("responsible_person","")}
"""

    md = f"""# 第二、三等級醫療器材查驗登記 / 許可證變更 — 申請資料（草稿）

## 申請填寫畫面－基本資料
- 填表日：{bd.get("fill_date","")}
- 公文收文日：{bd.get("received_date","")}
- 醫療器材：{bd.get("device_type","")}
- 案件種類：{bd.get("case_category","")}
- 案件類型：{bd.get("case_type","")}
- 許可證字號/分類分級品項：{bd.get("license_scope","")}
- 許可證號：{bd.get("license_number","")}
- 中文名稱：{bd.get("device_name_zh","")}
- 英文名稱：{bd.get("device_name_en","")}
- 風險等級：{bd.get("risk_class","")}
- 產地：{bd.get("origin","")}
- 有無類似品：{bd.get("has_similar_products","")}
- 替代：{bd.get("substitution","")}

## 類別（主分類/次分類）
{cls_table}

## 變更種類（矩陣）
{chg_table}

## 說明理由
{bd.get("change_reason","（未填）")}

## 申請商資料
- 統一編號：{ap.get("company_uniform_no","")}
- 醫療器材商名稱：{ap.get("company_name","")}
- 地址：{ap.get("company_address","")}
- 負責人姓名：{ap.get("responsible_person","")}
- 聯絡人姓名：{ap.get("contact_person","")}
- 電話：{ap.get("contact_phone","")}
- 電子郵件：{ap.get("contact_email","")}

{prev_block}

## 文件/附件勾選與檔案列
{att_table}

> ※提醒：本草稿由系統自動彙整，請申請人再次核對實際送件內容。
"""
    return md

# =========================
# Mock Data (3 applications + 3 guidances)
# =========================

MOCK_APPLICATIONS = {}
MOCK_GUIDANCES = {}

def load_mock_assets():
    # App 1 (IVD glucose meter change) - based on your pasted example
    MOCK_APPLICATIONS["範例1-血糖測試儀許可證變更"] = {
        "basic_data": {
            "fill_date": "2026-02-01",
            "received_date": "2026-02-02",
            "device_type": "體外診斷器材(IVD)",
            "case_category": "新案",
            "case_type": "許可證變更",
            "license_scope": "許可證號",
            "license_number": "衛署醫器製字 第 003404 號",
            "device_name_zh": "欣活語音血糖測試儀",
            "device_name_en": "GlucoSure VIVO Blood Glucose Meter",
            "risk_class": "第二等級",
            "origin": "國產",
            "has_similar_products": "有",
            "substitution": "否",
            "change_reason": "本次變更涉及中文/英文品名與標籤/說明書更新，並修訂部分規格文字敘述；產品技術原理不變。",
        },
        "classifications": [
            {"main_category": "A.臨床化學及臨床毒理學", "sub_category_code": "A.1345", "sub_category_name": "葡萄糖試驗系統"},
            {"main_category": "J.一般醫院及個人使用裝置", "sub_category_code": "J.9999", "sub_category_name": "其他（自我監測用血糖測試儀）"},
        ],
        "change_items": [
            {"change_item": "中文品名", "original_approval": "欣活語音血糖測試儀", "requested_change": "欣活語音血糖測試儀（新版包裝）"},
            {"change_item": "英文品名", "original_approval": "GlucoSure VIVO Blood Glucose Meter", "requested_change": "GlucoSure VIVO Voice Blood Glucose Meter"},
            {"change_item": "原廠標籤、說明書或包裝", "original_approval": "舊版中文說明書/外盒標籤", "requested_change": "新版中文說明書/外盒標籤（新增語音操作提示）"},
            {"change_item": "成分、材料、結構、規格或型號變更（未涉及安全及效能評估之尺寸規格變更）",
             "original_approval": "外觀尺寸 110×60×18mm",
             "requested_change": "外觀尺寸 112×60×18mm（外殼改版，不影響性能）"},
        ] + [{"change_item": x, "original_approval": "", "requested_change": ""} for x in DEFAULT_CHANGE_ROWS[4:]],
        "applicant": {
            "company_uniform_no": "16130182",
            "company_name": "五鼎生物技術股份有限公司",
            "company_address": "新竹市東區新竹科學工業園區力行五路 7 號",
            "responsible_person": "沈燕士",
            "contact_person": "黃蓓音",
            "contact_phone": "03-5641952 分機：507",
            "contact_email": "alishahuang@apexbio.com",
            "previous_values": {
                "company_uniform_no": "16130182",
                "company_name": "五鼎生物技術股份有限公司",
                "company_address": "新竹市東區新竹科學工業園區力行五路 7 號",
                "responsible_person": "沈燕士",
            }
        },
        "attachments": [
            {"section_id":"1","section_title":"一、醫療器材許可證變更登記申請書","applicability":"適用","notes":"已準備","files":[{"file_name":"變更登記申請書.pdf","status":"有效"}]},
            {"section_id":"2","section_title":"二、原核准文件（原許可證/騎縫章標籤、說明書或包裝）","applicability":"適用","notes":"","files":[{"file_name":"原許可證掃描.pdf","status":"有效"},{"file_name":"原核准標籤_說明書.pdf","status":"有效"}]},
            {"section_id":"4","section_title":"四、變更說明文件（比較表/原廠變更說明函）","applicability":"適用","notes":"含比較表與變更說明函","files":[{"file_name":"比較表.xlsx","status":"有效"},{"file_name":"原廠變更說明函.pdf","status":"有效"}]},
            {"section_id":"7","section_title":"七、出產國製售證明","applicability":"不適用","notes":"國產產品","files":[]},
            {"section_id":"9","section_title":"九、QMS/QSD 證明文件","applicability":"適用","notes":"ISO 13485 證書影本","files":[{"file_name":"ISO13485證書.pdf","status":"有效"}]},
            {"section_id":"11","section_title":"十一、標籤、說明書或包裝擬稿","applicability":"適用","notes":"含中文標籤與中文說明書擬稿","files":[
                {"file_name":"中文標籤_v2.pdf","status":"有效"},
                {"file_name":"中文說明書擬稿_v2.pdf","status":"有效"},
                {"file_name":"舊版操作手冊.pdf","status":"作廢"},
            ]},
        ] + [
            {"section_id": sid, "section_title": title, "applicability": "未判定", "notes": "", "files": []}
            for sid, title in DEFAULT_ATTACHMENTS
            if sid not in {"1","2","4","7","9","11"}
        ],
    }

    MOCK_GUIDANCES["範例1-血糖測試儀許可證變更"] = """# TFDA 形式審查/預審指引（範例1：許可證變更）

## 一、基本資料完整性
1. 申請畫面「填表日」「公文收文日」應填具，日期格式需一致（YYYY-MM-DD）。
2. 「醫療器材類型」「案件種類」「案件類型」「產地」「風險等級」為必填。
3. 若為「許可證變更」，須提供：
   - 許可證號（完整字號）
   - 變更種類矩陣（至少勾選/填寫 1 項具體變更）
   - 說明理由（清楚描述變更範圍、是否涉及安全/效能）

## 二、文件附件一致性
1. 變更登記申請書：必須適用（除遺失補發/汙損換發另有適用情形）。
2. 原核准文件（原許可證、原核准騎縫章標籤/說明書/包裝）：若涉及標籤/說明書變更，通常為必附。
3. 變更說明文件：
   - 應附「變更比較表」並清楚對照原核准與申請變更內容。
   - 應附「原廠變更說明函」（若為輸入品/原廠文件要求時）
4. QMS/QSD：依產品與案件類型判定；若適用應附有效證明。

## 三、常見缺漏/矛盾
- 變更理由僅寫「更新」但未說明具體更新點 → 判定「可能不足」。
- 變更涉及規格/軟體/性能敘述，但未提供風險評估或佐證 → 判定「明顯缺漏」。
- 附件勾選為「適用」但未列出檔案或檔案標示作廢未補新檔 → 判定「缺漏」。

> 關鍵詞：<span class="coral">必填</span>、<span class="coral">須提供</span>、<span class="coral">變更比較表</span>、<span class="coral">說明理由</span>
"""

    # App 2 (Orthopedic implant new class III)
    MOCK_APPLICATIONS["範例2-骨科植入物新案"] = {
        "basic_data": {
            "fill_date": "2026-01-20",
            "received_date": "2026-01-22",
            "device_type": "一般醫材",
            "case_category": "新案",
            "case_type": "查驗登記新案",
            "license_scope": "分類分級品項",
            "license_number": "",
            "device_name_zh": "鈦合金椎體間融合器",
            "device_name_en": "Titanium Interbody Fusion Cage",
            "risk_class": "第三等級",
            "origin": "輸入",
            "has_similar_products": "有",
            "substitution": "否",
            "change_reason": "不適用（新案）",
        },
        "classifications": [
            {"main_category":"N.骨科學","sub_category_code":"N.9999","sub_category_name":"其他（脊椎植入物）"}
        ],
        "change_items": [],
        "applicant": {
            "company_uniform_no": "24567890",
            "company_name": "海岳醫材股份有限公司",
            "company_address": "台北市內湖區瑞光路 88 號 10F",
            "responsible_person": "林俊傑",
            "contact_person": "張雅雯",
            "contact_phone": "02-8797-0000 分機 312",
            "contact_email": "regulatory@seamount-med.com",
            "previous_values": {}
        },
        "attachments": [
            {"section_id":"11","section_title":"十一、標籤、說明書或包裝擬稿","applicability":"適用","notes":"含中文標籤、U DI、使用方式與禁忌","files":[{"file_name":"中文說明書_v1.pdf","status":"有效"}]},
            {"section_id":"12","section_title":"十二、產品結構/材料/規格/性能/用途/圖樣","applicability":"適用","notes":"含材料證明、圖樣、規格","files":[{"file_name":"技術檔案_STED摘要.pdf","status":"有效"}]},
            {"section_id":"17","section_title":"十七、臨床前測試及原廠品質管制資料","applicability":"適用","notes":"含機械強度、疲勞測試、生物相容性摘要","files":[{"file_name":"BenchTestReport.pdf","status":"有效"}]},
            {"section_id":"18","section_title":"十八、臨床證據資料","applicability":"適用","notes":"文獻回顧 + 臨床評估報告","files":[{"file_name":"ClinicalEvaluationReport.pdf","status":"有效"}]},
        ] + [
            {"section_id": sid, "section_title": title, "applicability": "未判定", "notes": "", "files": []}
            for sid, title in DEFAULT_ATTACHMENTS
            if sid not in {"11","12","17","18"}
        ],
    }

    MOCK_GUIDANCES["範例2-骨科植入物新案"] = """# TFDA 審查重點指引（範例2：第三等級骨科植入物新案）

## 一、文件組成（新案）
1. 應具備完整中文標籤/說明書擬稿（含適應症、禁忌、警語、滅菌/保存資訊如適用）。
2. 應具備技術檔案（產品結構、材料、規格、製程資訊、圖樣、性能說明）。
3. 風險管理文件：應符合 ISO 14971 架構，含危害分析、風險控制與殘餘風險可接受性論證。
4. 生物相容性：依接觸性質/時間評估，提供對應試驗或充分理由（例如 ISO 10993 系列）。
5. 臨床證據：第三等級通常需較完整之臨床評估；若採文獻，需說明等同性/可比性。

## 二、常見缺漏
- 只提供宣告但缺少原始測試摘要/判讀 → <span class="coral">可能不足</span>
- 材料來源/表面處理未說明、未提供成分與製程一致性證據 → <span class="coral">明顯缺漏</span>
- 說明書與技術檔案不一致（規格、適應症、禁忌）→ <span class="coral">需釐清</span>

## 三、輸入品常見要求
- 原廠授權（如適用）
- 出產國製售證明（依案件/主管機關要求判定）
- QMS/QSD 證明（有效期限、涵蓋製造廠與產品範圍）

> 關鍵詞：<span class="coral">風險管理</span>、<span class="coral">生物相容性</span>、<span class="coral">臨床證據</span>、<span class="coral">一致性</span>
"""

    # App 3 (Software-heavy connected device)
    MOCK_APPLICATIONS["範例3-連網居家生理量測系統變更"] = {
        "basic_data": {
            "fill_date": "2026-01-10",
            "received_date": "2026-01-12",
            "device_type": "一般醫材",
            "case_category": "申復",
            "case_type": "許可證變更",
            "license_scope": "許可證號",
            "license_number": "衛部醫器製字第 009999 號",
            "device_name_zh": "居家連網血壓量測系統",
            "device_name_en": "Home Connected Blood Pressure Monitoring System",
            "risk_class": "第二等級",
            "origin": "國產",
            "has_similar_products": "有",
            "substitution": "否",
            "change_reason": "本次變更新增行動 App 之資安機制（帳號鎖定/加密傳輸）及修訂說明書資安警語；量測硬體不變。",
        },
        "classifications": [
            {"main_category":"J.一般醫院及個人使用裝置","sub_category_code":"J.9999","sub_category_name":"其他（居家量測/遠距傳輸）"}
        ],
        "change_items": [
            {"change_item":"原廠標籤、說明書或包裝","original_approval":"說明書 v1.0","requested_change":"說明書 v1.1（新增資安警語與帳號管理說明）"},
            {"change_item":"成分、材料、結構、規格或型號變更（涉及安全及效能評估）","original_approval":"App 未提供帳號鎖定","requested_change":"App 新增帳號鎖定與TLS傳輸，新增資安測試摘要"},
        ] + [{"change_item": x, "original_approval": "", "requested_change": ""} for x in DEFAULT_CHANGE_ROWS[2:]],
        "applicant": {
            "company_uniform_no": "11223344",
            "company_name": "康雲智慧醫療股份有限公司",
            "company_address": "台中市西屯區市政北二路 66 號 8F",
            "responsible_person": "許文豪",
            "contact_person": "陳怡君",
            "contact_phone": "04-2258-1234 分機 206",
            "contact_email": "qa-ra@healthcloud.tw",
            "previous_values": {"company_name":"康雲智慧醫療股份有限公司","company_uniform_no":"11223344","company_address":"台中市西屯區市政北二路 66 號 8F","responsible_person":"許文豪"}
        },
        "attachments": [
            {"section_id":"11","section_title":"十一、標籤、說明書或包裝擬稿","applicability":"適用","notes":"含資安警語","files":[{"file_name":"中文說明書_v1.1.pdf","status":"有效"}]},
            {"section_id":"17","section_title":"十七、臨床前測試及原廠品質管制資料","applicability":"適用","notes":"含軟體確效/資安測試摘要","files":[{"file_name":"SoftwareVnV_Summary.pdf","status":"有效"},{"file_name":"Cybersecurity_Test_Summary.pdf","status":"有效"}]},
        ] + [
            {"section_id": sid, "section_title": title, "applicability": "未判定", "notes": "", "files": []}
            for sid, title in DEFAULT_ATTACHMENTS
            if sid not in {"11","17"}
        ],
    }

    MOCK_GUIDANCES["範例3-連網居家生理量測系統變更"] = """# TFDA 審查指引（範例3：連網/軟體變更重點）

## 一、變更案件基本要求
1. 變更理由需明確說明：變更範圍、變更原因、是否影響安全/效能。
2. 若涉及軟體/連網功能，應提供：
   - 軟體版本、修訂歷史（Revision Level History）
   - 風險分析（含資安風險）
   - V&V（查證與確認）摘要與結論
3. 說明書更新需與實際功能一致，並加入必要警語（例如帳號管理、密碼強度、更新機制）。

## 二、資安（Cybersecurity）最低期待
- 需描述資料流、加密策略、身分驗證與存取控制。
- 需說明弱點管理與更新機制（例如 OTA 更新流程）。
- 若宣稱符合特定標準/指引，需提供對應佐證或測試摘要。

## 三、常見缺漏
- 僅敘述「新增加密」但無具體演算法/適用範圍/測試結果 → <span class="coral">可能不足</span>
- 軟體需求規格（SRS）與測試案例缺乏追溯性（Traceability） → <span class="coral">明顯缺漏</span>
- 說明書未更新資安使用者責任與警語 → <span class="coral">需補充</span>

> 關鍵詞：<span class="coral">資安</span>、<span class="coral">V&V</span>、<span class="coral">追溯性</span>、<span class="coral">版本</span>
"""

load_mock_assets()

def apply_mock_to_session(name: str):
    init_tw_application_if_missing()
    st.session_state["tw_application"] = json.loads(json.dumps(MOCK_APPLICATIONS[name], ensure_ascii=False))
    st.session_state["tw_guidance_text"] = MOCK_GUIDANCES.get(name, "")
    st.session_state["tw_app_markdown"] = render_tw_application_markdown(st.session_state["tw_application"])

# =========================
# Sidebar
# =========================

def render_sidebar():
    with st.sidebar:
        st.markdown("## Global Settings")

        st.session_state.settings["theme"] = st.radio(
            "Theme", ["Light", "Dark"],
            index=0 if st.session_state.settings["theme"] == "Light" else 1,
        )
        st.session_state.settings["language"] = st.radio(
            "Language", ["English", "繁體中文"],
            index=0 if st.session_state.settings["language"] == "English" else 1,
        )

        col1, col2 = st.columns([3, 1])
        with col1:
            style = st.selectbox(
                "Painter Style",
                PAINTER_STYLES,
                index=PAINTER_STYLES.index(st.session_state.settings["painter_style"]),
            )
        with col2:
            if st.button("Jackpot!"):
                style = random.choice(PAINTER_STYLES)
        st.session_state.settings["painter_style"] = style

        st.session_state.settings["model"] = st.selectbox(
            "Default Model",
            ALL_MODELS,
            index=ALL_MODELS.index(st.session_state.settings["model"]),
        )
        st.session_state.settings["max_tokens"] = st.number_input(
            "Default max_tokens",
            min_value=1000, max_value=120000,
            value=int(st.session_state.settings["max_tokens"]),
            step=1000,
        )
        st.session_state.settings["temperature"] = st.slider(
            "Temperature", 0.0, 1.0, float(st.session_state.settings["temperature"]), 0.05
        )

        st.markdown("---")
        st.markdown("## API Keys")

        keys = {}

        if os.getenv("OPENAI_API_KEY"):
            keys["openai"] = os.getenv("OPENAI_API_KEY")
            st.caption("OpenAI key from environment.")
        else:
            keys["openai"] = st.text_input("OpenAI API Key", type="password")

        if os.getenv("GEMINI_API_KEY"):
            keys["gemini"] = os.getenv("GEMINI_API_KEY")
            st.caption("Gemini key from environment.")
        else:
            keys["gemini"] = st.text_input("Gemini API Key", type="password")

        if os.getenv("ANTHROPIC_API_KEY"):
            keys["anthropic"] = os.getenv("ANTHROPIC_API_KEY")
            st.caption("Anthropic key from environment.")
        else:
            keys["anthropic"] = st.text_input("Anthropic API Key", type="password")

        if os.getenv("GROK_API_KEY"):
            keys["grok"] = os.getenv("GROK_API_KEY")
            st.caption("Grok key from environment.")
        else:
            keys["grok"] = st.text_input("Grok API Key", type="password")

        st.session_state["api_keys"] = keys

        st.markdown("---")
        st.markdown("## Demo / Mock Data")

        mock_names = list(MOCK_APPLICATIONS.keys())
        pick = st.selectbox("Load mock application", ["（不載入）"] + mock_names, index=0)
        if pick != "（不載入）":
            if st.button("Load selected mock into TW Premarket"):
                apply_mock_to_session(pick)
                st.success("已載入 mock 申請資料與對應指引。")

        st.markdown("---")
        st.markdown("## agents.yaml (optional)")
        uploaded_agents = st.file_uploader("Upload custom agents.yaml", type=["yaml", "yml"])
        if uploaded_agents is not None:
            try:
                cfg = yaml.safe_load(uploaded_agents.read())
                if "agents" in cfg:
                    st.session_state["agents_cfg"] = cfg
                    st.success("Custom agents.yaml loaded for this session.")
                else:
                    st.warning("Uploaded YAML has no top-level 'agents' key.")
            except Exception as e:
                st.error(f"Failed to parse uploaded YAML: {e}")

# =========================
# Dashboard
# =========================

def render_dashboard():
    st.title(t("Dashboard"))
    hist = st.session_state["history"]
    if not hist:
        st.info("No runs yet.")
        return

    df = pd.DataFrame(hist)

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Total Runs", len(df))
    with col2: st.metric("Unique Tabs", df["tab"].nunique())
    with col3: st.metric("Approx Tokens Processed", int(df["tokens_est"].sum()))

    st.markdown("### WOW Status Wall – Latest Activity")
    last = df.sort_values("ts", ascending=False).iloc[0]
    wow_color = "linear-gradient(135deg,#22c55e,#16a34a)"
    if last["tokens_est"] > 40000: wow_color = "linear-gradient(135deg,#f97316,#ea580c)"
    if last["tokens_est"] > 80000: wow_color = "linear-gradient(135deg,#ef4444,#b91c1c)"

    st.markdown(
        f"""
        <div class="wow-card" style="background:{wow_color}; color:white;">
          <div class="wow-card-title">LATEST RUN SNAPSHOT</div>
          <div class="wow-card-main">{last['tab']} · {last['agent']}</div>
          <div style="margin-top:6px;font-size:0.92rem;">
            Model: <b>{last['model']}</b> · Tokens ≈ <b>{last['tokens_est']}</b><br>
            Time (UTC): {last['ts']}
          </div>
          <div style="margin-top:8px;"><span class="wow-badge">Status: active</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Runs by Tab")
    st.altair_chart(
        alt.Chart(df).mark_bar().encode(x="tab:N", y="count():Q", color="tab:N", tooltip=["tab", "count()"]),
        use_container_width=True,
    )

    st.markdown("### Runs by Model")
    st.altair_chart(
        alt.Chart(df).mark_bar().encode(x="model:N", y="count():Q", color="model:N", tooltip=["model", "count()"]),
        use_container_width=True,
    )

    st.markdown("### Model × Tab Usage Heatmap")
    heat_df = df.groupby(["tab", "model"]).size().reset_index(name="count")
    heatmap = alt.Chart(heat_df).mark_rect().encode(
        x=alt.X("model:N", title="Model"),
        y=alt.Y("tab:N", title="Tab"),
        color=alt.Color("count:Q", scale=alt.Scale(scheme="blues")),
        tooltip=["tab", "model", "count"],
    ).properties(height=260)
    st.altair_chart(heatmap, use_container_width=True)

    st.markdown("### Recent Activity")
    st.dataframe(df.sort_values("ts", ascending=False).head(25), use_container_width=True)

# =========================
# TW Premarket Tab (PDF-aligned basic data form)
# =========================

def render_tw_premarket_tab():
    init_tw_application_if_missing()
    app = st.session_state["tw_application"]

    st.title(t("TW Premarket"))

    score, missing = tw_completeness_score(app)
    pct = int(score * 100)
    if pct >= 80:
        card_grad = "linear-gradient(135deg,#22c55e,#16a34a)"; txt = "基本欄位完成度高，適合進行預審。"
    elif pct >= 50:
        card_grad = "linear-gradient(135deg,#f97316,#ea580c)"; txt = "部分關鍵欄位仍待補齊，建議補足後再送預審。"
    else:
        card_grad = "linear-gradient(135deg,#ef4444,#b91c1c)"; txt = "多數基本欄位尚未填寫，請先充實申請資訊。"

    st.markdown(
        f"""
        <div class="wow-card" style="background:{card_grad}; color:white;">
          <div class="wow-card-title">APPLICATION COMPLETENESS</div>
          <div class="wow-card-main">{pct}%</div>
          <div style="margin-top:6px;font-size:0.92rem;">{txt}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(score)
    if missing:
        st.warning("尚缺欄位：\n- " + "\n- ".join(missing))

    st.markdown("---")
    st.markdown("## Step 1 – 申請填寫畫面（基本資料）")

    bd = app["basic_data"]
    col1, col2 = st.columns(2)
    with col1:
        fill_date = st.date_input("填表日 *", value=date.fromisoformat(bd["fill_date"]) if bd["fill_date"] else date.today())
    with col2:
        received_date = st.date_input("公文收文日 *", value=date.fromisoformat(bd["received_date"]) if bd["received_date"] else date.today())

    bd["fill_date"] = fill_date.isoformat()
    bd["received_date"] = received_date.isoformat()

    col3, col4, col5 = st.columns(3)
    with col3:
        bd["device_type"] = st.radio("醫療器材 *", ["一般醫材", "體外診斷器材(IVD)"], index=0 if bd["device_type"]=="一般醫材" else 1)
    with col4:
        bd["case_category"] = st.radio("案件種類 *", ["新案", "申復"], index=0 if bd["case_category"]=="新案" else 1)
    with col5:
        bd["case_type"] = st.selectbox("案件類型 *", ["許可證變更", "查驗登記新案", "許可證變更（補件）", "其它"], index=0)

    col6, col7 = st.columns(2)
    with col6:
        bd["license_scope"] = st.selectbox("許可證字號 / 分類分級品項 *", ["許可證號", "分類分級品項"], index=0 if bd["license_scope"]=="許可證號" else 1)
    with col7:
        bd["license_number"] = st.text_input("許可證號（許可證變更常見必填）", value=bd.get("license_number",""))

    st.markdown("### 產品資訊")
    col8, col9, col10 = st.columns(3)
    with col8:
        bd["device_name_zh"] = st.text_input("中文名稱 *", value=bd.get("device_name_zh",""))
    with col9:
        bd["device_name_en"] = st.text_input("英文名稱 *", value=bd.get("device_name_en",""))
    with col10:
        bd["risk_class"] = st.radio("風險等級 *", ["第二等級", "第三等級"], index=0 if bd.get("risk_class")=="第二等級" else 1)

    st.markdown("### 類別（主分類/次分類/操作）")
    cls_df = pd.DataFrame(app.get("classifications", []))
    if cls_df.empty:
        cls_df = pd.DataFrame([{"main_category":"", "sub_category_code":"", "sub_category_name":""}])
    edited_cls = st.data_editor(
        cls_df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "main_category": st.column_config.SelectboxColumn("主分類", options=MAIN_CATEGORIES),
            "sub_category_code": st.column_config.TextColumn("次分類代碼（例：A.1225）"),
            "sub_category_name": st.column_config.TextColumn("次分類名稱（例：肌氨酸酐試驗系統）"),
        },
        key="tw_cls_editor"
    )
    app["classifications"] = edited_cls.fillna("").to_dict(orient="records")

    st.markdown("### 產地 / 類似品 / 替代")
    col11, col12, col13 = st.columns(3)
    with col11:
        bd["origin"] = st.radio("產地 *", ["國產", "輸入", "陸輸"], index=["國產","輸入","陸輸"].index(bd.get("origin","國產")))
    with col12:
        bd["has_similar_products"] = st.radio("有無類似品 *", ["有", "無", "全球首創", "非新增/變更規格"],
                                              index=["有","無","全球首創","非新增/變更規格"].index(bd.get("has_similar_products","有")))
    with col13:
        bd["substitution"] = st.radio("替代 *", ["是", "否", "非新增/變更規格"], index=["是","否","非新增/變更規格"].index(bd.get("substitution","否")))

    st.markdown("### 變更種類（項目 / 原核准登記事項 / 申請變更事項）")
    chg_df = pd.DataFrame(app.get("change_items", []))
    if chg_df.empty:
        chg_df = pd.DataFrame([{"change_item":"", "original_approval":"", "requested_change":""}])
    edited_chg = st.data_editor(
        chg_df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "change_item": st.column_config.TextColumn("項目"),
            "original_approval": st.column_config.TextColumn("原核准登記事項"),
            "requested_change": st.column_config.TextColumn("申請變更事項"),
        },
        key="tw_change_editor"
    )
    app["change_items"] = edited_chg.fillna("").to_dict(orient="records")

    bd["change_reason"] = st.text_area("說明理由 *（許可證變更必填）", value=bd.get("change_reason",""), height=120)

    st.markdown("## 申請商資料")
    ap = app["applicant"]
    colA, colB = st.columns(2)
    with colA:
        ap["company_uniform_no"] = st.text_input("統一編號 *", value=ap.get("company_uniform_no",""))
        ap["company_name"] = st.text_input("醫療器材商名稱 *", value=ap.get("company_name",""))
        ap["company_address"] = st.text_area("地址 *", value=ap.get("company_address",""), height=80)
    with colB:
        ap["responsible_person"] = st.text_input("負責人姓名 *", value=ap.get("responsible_person",""))
        ap["contact_person"] = st.text_input("聯絡人姓名 *", value=ap.get("contact_person",""))
        ap["contact_phone"] = st.text_input("電話 *", value=ap.get("contact_phone",""))
        ap["contact_email"] = st.text_input("電子郵件 *", value=ap.get("contact_email",""))

    show_prev = st.checkbox("顯示修正前資訊（如適用）", value=False)
    if show_prev:
        prev = ap.get("previous_values", {})
        st.markdown("### 修正前（如適用）")
        colP, colQ = st.columns(2)
        with colP:
            prev["company_uniform_no"] = st.text_input("修正前：統一編號", value=prev.get("company_uniform_no",""), key="prev_u")
            prev["company_name"] = st.text_input("修正前：醫療器材商名稱", value=prev.get("company_name",""), key="prev_n")
        with colQ:
            prev["company_address"] = st.text_area("修正前：地址", value=prev.get("company_address",""), height=70, key="prev_a")
            prev["responsible_person"] = st.text_input("修正前：負責人姓名", value=prev.get("responsible_person",""), key="prev_r")
        ap["previous_values"] = prev

    st.markdown("## 文件/附件勾選（適用/不適用/未判定）")
    att_df = pd.DataFrame([
        {
            "section_id": x["section_id"],
            "section_title": x["section_title"],
            "applicability": x["applicability"],
            "notes": x.get("notes",""),
        } for x in app.get("attachments", [])
    ])
    edited_att = st.data_editor(
        att_df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "applicability": st.column_config.SelectboxColumn("勾選", options=["適用","不適用","未判定"]),
        },
        key="tw_att_editor"
    )

    # merge back while preserving files
    old_map = {(x["section_id"], x["section_title"]): x for x in app.get("attachments", [])}
    new_list = []
    for _, r in edited_att.fillna("").iterrows():
        k = (str(r["section_id"]), str(r["section_title"]))
        base = old_map.get(k, {"files":[]})
        base.update({
            "section_id": str(r["section_id"]),
            "section_title": str(r["section_title"]),
            "applicability": str(r["applicability"]),
            "notes": str(r["notes"]),
        })
        if "files" not in base:
            base["files"] = []
        new_list.append(base)
    app["attachments"] = new_list

    with st.expander("檔案列（可逐節次記錄檔案名稱/狀態，如：作廢）", expanded=False):
        sec_ids = [f'{x["section_id"]} - {x["section_title"]}' for x in app["attachments"]]
        pick_sec = st.selectbox("選擇節次", sec_ids, index=0 if sec_ids else None)
        if sec_ids:
            idx = sec_ids.index(pick_sec)
            files_df = pd.DataFrame(app["attachments"][idx].get("files", []))
            if files_df.empty:
                files_df = pd.DataFrame([{"file_name":"", "status":"有效"}])
            edited_files = st.data_editor(
                files_df,
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "status": st.column_config.SelectboxColumn("狀態", options=["有效","作廢","待補","未知"]),
                    "file_name": st.column_config.TextColumn("檔案名稱"),
                },
                key="tw_files_editor"
            )
            app["attachments"][idx]["files"] = edited_files.fillna("").to_dict(orient="records")

    st.markdown("---")
    st.markdown("## Step 2 – 生成申請書 Markdown 草稿（可編輯）")

    colg1, colg2, colg3 = st.columns([1,1,1])
    with colg1:
        if st.button("生成/更新申請書 Markdown 草稿"):
            st.session_state["tw_app_markdown"] = render_tw_application_markdown(app)
            st.success("已生成草稿。")
    with colg2:
        json_bytes = json.dumps(app, ensure_ascii=False, indent=2).encode("utf-8")
        st.download_button("下載申請資料 JSON", data=json_bytes, file_name="tw_application.json", mime="application/json")
    with colg3:
        if st.button("重設（清空）本頁資料"):
            if "tw_application" in st.session_state:
                del st.session_state["tw_application"]
            init_tw_application_if_missing()
            st.rerun()

    md_current = st.session_state.get("tw_app_markdown", render_tw_application_markdown(app))
    st.session_state["tw_app_markdown"] = md_current

    view = st.radio("檢視模式", ["Markdown", "純文字"], horizontal=True)
    md_edited = st.text_area("申請書內容（可修改）", value=md_current, height=320)
    st.session_state["tw_app_effective_md"] = md_edited

    st.markdown("---")
    st.markdown("## Step 3 – 輸入預審/形式審查指引（Review Guidance）")

    colG1, colG2 = st.columns(2)
    with colG1:
        gfile = st.file_uploader("上傳指引（PDF/TXT/MD）", type=["pdf","txt","md"])
        gtext_file = ""
        if gfile is not None:
            suffix = gfile.name.lower().rsplit(".",1)[-1]
            if suffix == "pdf":
                gtext_file = extract_pdf_pages_to_text(gfile, 1, 9999)
            else:
                gtext_file = gfile.read().decode("utf-8", errors="ignore")
    with colG2:
        gtext_manual = st.text_area("或直接貼上指引文字/Markdown", value=st.session_state.get("tw_guidance_text",""), height=220)

    guidance_text = gtext_file or gtext_manual
    st.session_state["tw_guidance_text"] = guidance_text

    if guidance_text.strip():
        st.success("已載入指引。")
    else:
        st.info("尚未提供指引。可先用一般常規進行形式檢核。")

    st.markdown("---")
    st.markdown("## Step 4 – 形式審查/完整性檢核（Agent）")

    combined_input = f"""=== 申請書草稿（Markdown）===
{st.session_state.get("tw_app_effective_md","")}

=== 預審/形式審查指引（文字/Markdown）===
{guidance_text or "（尚未提供指引，請依一般法規常規進行形式檢核）"}
"""

    default_screen_prompt = """你是一位熟悉臺灣第二、三等級醫療器材查驗登記/許可證變更的形式審查（預審）審查員。

請根據輸入的「申請書草稿」與「預審/形式審查指引」，以繁體中文 Markdown 輸出：

1) 形式完整性檢核表
- 列出主要文件類別（申請書、原核准文件、比較表、原廠變更說明函、QMS/QSD、標籤/說明書擬稿、技術檔案、臨床前測試、軟體確效/資安、臨床證據等）
- 對每一項標示：預期應附？/ 申請書是否提及？/ 整體判定（足夠/可能不足/明顯缺漏）/ 備註

2) 重要欄位檢核
- 檢查必填欄位是否缺漏或矛盾（日期、許可證號、分類分級品項、變更矩陣、說明理由、申請商資料）

3) 預審評語摘要（300–600字）
- 分為「必須補件」與「建議補充」

4) 不要臆測；無從判斷請寫「依現有輸入無法判斷」。
"""

    agent_run_ui(
        agent_id="tw_screen_review_agent",
        tab_key="tw_screen",
        default_prompt=default_screen_prompt,
        default_input_text=combined_input,
        allow_model_override=True,
        tab_label_for_history="TW Premarket Screen Review",
    )

    st.markdown("---")
    st.markdown("## Step 5 – AI 協助編修申請書內容（Agent）")

    helper_prompt = """你是一位協助臺灣醫療器材查驗登記申請人撰寫文件的助手。

請在不新增未提供的技術/臨床事實前提下：
1) 優化 Markdown 結構與標題層級
2) 修正文句不通順之處
3) 對資訊不足處以「※待補：...」標註
輸出為 Markdown。
"""
    agent_run_ui(
        agent_id="tw_app_doc_helper",
        tab_key="tw_helper",
        default_prompt=helper_prompt,
        default_input_text=st.session_state.get("tw_app_effective_md",""),
        allow_model_override=True,
        tab_label_for_history="TW Application Doc Helper",
    )

# =========================
# Other tabs (preserved, concise)
# =========================

def render_510k_tab():
    st.title(t("510k_tab"))
    col1, col2 = st.columns(2)
    with col1:
        device_name = st.text_input("Device Name")
        k_number = st.text_input("510(k) Number (e.g., K123456)")
    with col2:
        sponsor = st.text_input("Sponsor / Manufacturer (optional)")
        product_code = st.text_input("Product Code (optional)")
    extra_info = st.text_area("Additional context (indications, technology, etc.)")

    default_prompt = f"""
你是一位 FDA 510(k) 審查支援分析師。

任務：
1) 彙整（或以公開資訊推演形式）裝置資訊，並以審查導向角度撰寫完整摘要（約 1500–2500 字）。
2) 提供至少 3 個 Markdown 表格：裝置概述、適應症/用途、性能測試與風險。

語言：{st.session_state.settings["language"]}
"""
    combined_input = f"""
Device: {device_name}
510(k): {k_number}
Sponsor: {sponsor}
Product code: {product_code}

Additional context:
{extra_info}
"""
    agent_run_ui(
        agent_id="fda_510k_intel_agent",
        tab_key="k510",
        default_prompt=default_prompt,
        default_input_text=combined_input,
        tab_label_for_history="510(k) Intelligence",
    )

def render_pdf_to_md_tab():
    st.title(t("PDF → Markdown"))
    uploaded = st.file_uploader("Upload PDF to convert selected pages to Markdown", type=["pdf"])
    if uploaded:
        col1, col2 = st.columns(2)
        with col1:
            p1 = st.number_input("From page", min_value=1, value=1)
        with col2:
            p2 = st.number_input("To page", min_value=1, value=5)
        if st.button("Extract Text"):
            st.session_state["pdf_raw_text"] = extract_pdf_pages_to_text(uploaded, int(p1), int(p2))

    raw_text = st.session_state.get("pdf_raw_text", "")
    if raw_text:
        default_prompt = f"""
你正在將法規/指引 PDF 的文字轉換成乾淨的 Markdown。
- 儘量保留標題、條列、表格（以 Markdown 表格呈現）
- 不要捏造未出現內容
語言：{st.session_state.settings["language"]}
"""
        agent_run_ui(
            agent_id="pdf_to_markdown_agent",
            tab_key="pdf2md",
            default_prompt=default_prompt,
            default_input_text=raw_text,
            tab_label_for_history="PDF → Markdown",
        )
    else:
        st.info("Upload a PDF and click 'Extract Text' to begin.")

def render_510k_review_pipeline_tab():
    st.title(t("Checklist & Report"))
    st.markdown("### Step 1 – Submission → Structured Markdown")
    raw_subm = st.text_area("Paste 510(k) submission material (text/markdown)", height=200)

    if st.button("Structure Submission"):
        if not raw_subm.strip():
            st.warning("Please paste submission material first.")
        else:
            api_keys = st.session_state.get("api_keys", {})
            user_prompt = "請將以下 510(k) 送件資料重新整理成結構化 Markdown（不要新增事實）。\n\n" + raw_subm
            out = call_llm(
                model=st.session_state.settings["model"],
                system_prompt="You structure a 510(k) submission.",
                user_prompt=user_prompt,
                max_tokens=st.session_state.settings["max_tokens"],
                temperature=0.15,
                api_keys=api_keys,
            )
            st.session_state["subm_struct_md"] = out
            log_event("510(k) Review Pipeline", "Submission Structurer", st.session_state.settings["model"], int(len(user_prompt+out)/4))

    subm_md = st.session_state.get("subm_struct_md", "")
    st.text_area("Structured Submission (editable)", value=subm_md, height=220)

    st.markdown("---")
    st.markdown("### Step 2 – Checklist & Step 3 – Review Report")
    chk_md = st.text_area("Paste checklist (markdown or text)", height=200)

    if st.button("Build Review Report"):
        if not subm_md.strip() or not chk_md.strip():
            st.warning("Need both structured submission and checklist.")
        else:
            api_keys = st.session_state.get("api_keys", {})
            user_prompt = f"""你是一位 FDA 510(k) 內部審查 memo 撰寫者。
請依 checklist 與 submission 產出審查報告（含結論與建議）。

=== CHECKLIST ===
{chk_md}

=== SUBMISSION ===
{subm_md}
"""
            out = call_llm(
                model=st.session_state.settings["model"],
                system_prompt="You are an FDA 510(k) reviewer.",
                user_prompt=user_prompt,
                max_tokens=st.session_state.settings["max_tokens"],
                temperature=0.18,
                api_keys=api_keys,
            )
            st.session_state["rep_md"] = out
            log_event("510(k) Review Pipeline", "Review Memo Builder", st.session_state.settings["model"], int(len(user_prompt+out)/4))

    rep_md = st.session_state.get("rep_md", "")
    st.text_area("Review Report (editable)", value=rep_md, height=260)

def render_note_keeper_tab():
    st.title(t("Note Keeper & Magics"))

    st.markdown("### Step 1 – Paste Notes & Transform to Structured Markdown")
    raw_notes = st.text_area("Paste your notes (text or markdown)", height=220, key="notes_raw")

    col1, col2 = st.columns(2)
    with col1:
        note_model = st.selectbox("Model", ALL_MODELS, index=ALL_MODELS.index(st.session_state.settings["model"]))
    with col2:
        note_max_tokens = st.number_input("max_tokens", min_value=2000, max_value=120000, value=12000, step=1000)

    default_prompt = """你是一位協助醫療器材/TFDA/510(k) 審查員整理筆記的助手。
請將筆記整理成清晰 Markdown（標題/條列），不要新增未提供的事實。
並列出「關鍵字」清單（10–25個）。
"""
    prompt = st.text_area("Prompt", value=default_prompt, height=150)

    if st.button("Transform notes"):
        if not raw_notes.strip():
            st.warning("Please paste notes first.")
        else:
            api_keys = st.session_state.get("api_keys", {})
            user_prompt = prompt + "\n\n=== NOTES ===\n" + raw_notes
            out = call_llm(
                model=note_model,
                system_prompt="You organize notes into clean markdown.",
                user_prompt=user_prompt,
                max_tokens=note_max_tokens,
                temperature=0.15,
                api_keys=api_keys,
            )
            st.session_state["note_md"] = out
            log_event("Note Keeper", "Note Structurer", note_model, int(len(user_prompt+out)/4))

    base_note = st.session_state.get("note_md", raw_notes)
    st.text_area("Structured Note (editable)", value=base_note, height=260, key="note_edit")

    st.markdown("---")
    st.markdown("### Magic – AI Keywords (Manual highlight)")
    kw = st.text_input("Keywords (comma-separated)", value="TFDA, 510(k), QMS, 生物相容性, IEC60601-1, IEC62304")
    color = st.color_picker("Color", "#ff7f50")
    if st.button("Apply Keyword Highlighting"):
        highlighted = highlight_keywords_simple(base_note, [x.strip() for x in kw.split(",")], color=color)
        st.markdown(highlighted, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Magic – AI Risk Flags（風險旗標）")
    risk_model = st.selectbox("Model (Risk)", ALL_MODELS, index=ALL_MODELS.index("gpt-4o-mini") if "gpt-4o-mini" in ALL_MODELS else 0, key="risk_model")
    risk_prompt = st.text_area(
        "Prompt (Risk)",
        value="請從以下筆記中偵測可能的法規/技術風險點，輸出 Markdown 表格：風險、嚴重度(高/中/低)、原因、建議措施。",
        height=120,
        key="risk_prompt"
    )
    if st.button("Run Risk Flags"):
        api_keys = st.session_state.get("api_keys", {})
        user_prompt = risk_prompt + "\n\n=== NOTE ===\n" + base_note
        out = call_llm(
            model=risk_model,
            system_prompt="You extract regulatory risk flags.",
            user_prompt=user_prompt,
            max_tokens=12000,
            temperature=0.2,
            api_keys=api_keys
        )
        st.text_area("Risk Register", value=out, height=240)

def render_agents_config_tab():
    st.title(t("Agents Config"))
    agents_cfg = st.session_state.get("agents_cfg", {"agents": {}})
    agents_dict = agents_cfg.get("agents", {})

    st.subheader("Agents Overview")
    if agents_dict:
        df = pd.DataFrame([{
            "agent_id": aid,
            "name": acfg.get("name",""),
            "model": acfg.get("model",""),
            "category": acfg.get("category",""),
        } for aid, acfg in agents_dict.items()])
        st.dataframe(df, use_container_width=True, height=240)
    else:
        st.warning("No agents found in current agents.yaml.")

    st.markdown("---")
    st.subheader("Edit agents.yaml (raw)")

    yaml_str = yaml.dump(st.session_state["agents_cfg"], allow_unicode=True, sort_keys=False)
    edited = st.text_area("agents.yaml", value=yaml_str, height=320)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Apply YAML"):
            try:
                cfg = yaml.safe_load(edited)
                if not isinstance(cfg, dict) or "agents" not in cfg:
                    st.error("YAML must contain top-level 'agents'.")
                else:
                    st.session_state["agents_cfg"] = cfg
                    st.success("Applied.")
            except Exception as e:
                st.error(f"Parse error: {e}")
    with col2:
        st.download_button("Download agents.yaml", data=yaml_str.encode("utf-8"), file_name="agents.yaml", mime="text/yaml")

# =========================
# Boot
# =========================

st.set_page_config(page_title="Agentic Medical Device Reviewer (WOW)", layout="wide")

if "settings" not in st.session_state:
    st.session_state["settings"] = {
        "theme": "Light",
        "language": "繁體中文",
        "painter_style": "Van Gogh",
        "model": "gpt-4o-mini",
        "max_tokens": 12000,
        "temperature": 0.2,
    }
if "history" not in st.session_state:
    st.session_state["history"] = []

if "agents_cfg" not in st.session_state:
    try:
        with open("agents.yaml", "r", encoding="utf-8") as f:
            st.session_state["agents_cfg"] = yaml.safe_load(f)
    except Exception:
        st.session_state["agents_cfg"] = {
            "agents": {
                "tw_screen_review_agent": {
                    "name": "TFDA 預審形式審查代理",
                    "model": "gemini-2.5-flash",
                    "system_prompt": "You are a TFDA premarket screen reviewer.",
                    "max_tokens": 12000,
                    "category": "TFDA Premarket",
                },
                "tw_app_doc_helper": {
                    "name": "TFDA 申請書撰寫助手",
                    "model": "gpt-4o-mini",
                    "system_prompt": "You help improve TFDA application documents.",
                    "max_tokens": 12000,
                    "category": "TFDA Premarket",
                },
                "pdf_to_markdown_agent": {
                    "name": "PDF to Markdown Agent",
                    "model": "gemini-2.5-flash",
                    "system_prompt": "You convert PDF-extracted text into clean markdown.",
                    "max_tokens": 12000,
                    "category": "文件前處理",
                },
                "fda_510k_intel_agent": {
                    "name": "510(k) Intelligence Agent",
                    "model": "gpt-4o-mini",
                    "system_prompt": "You are an FDA 510(k) analyst.",
                    "max_tokens": 12000,
                    "category": "FDA 510(k)",
                },
            }
        }

render_sidebar()
apply_style(st.session_state.settings["theme"], st.session_state.settings["painter_style"])

tabs = st.tabs([
    t("Dashboard"),
    t("TW Premarket"),
    t("510k_tab"),
    t("PDF → Markdown"),
    t("Checklist & Report"),
    t("Note Keeper & Magics"),
    t("Agents Config"),
])

with tabs[0]: render_dashboard()
with tabs[1]: render_tw_premarket_tab()
with tabs[2]: render_510k_tab()
with tabs[3]: render_pdf_to_md_tab()
with tabs[4]: render_510k_review_pipeline_tab()
with tabs[5]: render_note_keeper_tab()
with tabs[6]: render_agents_config_tab()
