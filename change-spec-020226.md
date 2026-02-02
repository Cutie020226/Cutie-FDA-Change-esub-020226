# Technical Specification (Improved): Advanced Medical Device Application & Agentic Review System  
**Target platform:** Hugging Face Spaces (Streamlit)  
**LLM providers:** OpenAI, Google Gemini, Anthropic, Grok (xAI)  
**Config:** `agents.yaml`, `SKILL.md` (editable via UI)  
**Key enhancement in this revision:** Add a **TFDA “Application Fill-in Screen – Basic Data”** application form module **aligned to the attached PDF/screenshots content**, while **retaining all existing features** and adding the requested WOW UI/agent controls/Note Keeper improvements.

---

## 1. Purpose & Scope

This specification defines an upgraded regulatory workflow system that supports:

1. **TFDA (Taiwan) Class II/III submission preparation and screening** (including “許可證變更” flows shown in the provided form screenshots).
2. **FDA 510(k) intelligence + review pipeline** (existing feature preserved).
3. **Guidance ingestion & conversion (PDF→Markdown + keyword highlighting)** (existing feature preserved).
4. **Agentic execution where users can:**
   - Select models from a multi-provider catalog
   - Edit prompts and `max_tokens` (default 12000)
   - Run agents **one-by-one**, editing each output (text or markdown) as input to the next agent (existing capability, expanded as a first-class “Agent Runner” pattern across tabs).
5. **AI Note Keeper + AI Magics** to organize notes and apply advanced transformations (existing feature expanded).

This revision specifically adds an **application form experience** that mirrors the “申請填寫畫面-基本資料” UI structure the user pasted (fields such as 填表日、公文收文日、醫療器材類型、案件種類、案件類型、許可證字號、中文/英文名稱、風險等級、類別主分類/次分類、產地、變更種類明細、說明理由、有無類似品、替代、申請商資料，以及文件/附件清單與適用性勾選狀態等).

---

## 2. System Overview

### 2.1 Core User Journeys (End-to-End)

#### A) TFDA Application (Basic Data → Document Set → Screen Review)
1. User selects **TW Premarket** workspace.
2. User fills **Basic Data form** (new) mirroring the official “Basic Data” screen.
3. User optionally imports from **JSON/CSV** or **OCR-assisted PDF/image extraction** to auto-populate the form.
4. User attaches or records **required document checklist** items and upload evidence (optional; metadata + file list).
5. User clicks **Generate Application Markdown Draft** (existing feature, improved to reflect new fields and tables).
6. User loads **screening guidance** (PDF/TXT/MD) and runs **TW Screen Review Agent**.
7. User edits agent output and optionally runs follow-up agents (rewrite, gap list, action plan).

#### B) Guidance Lab
- Upload guidance PDF; trim pages; extract text; optional LLM-Vision OCR; convert to Markdown; highlight keywords in coral; edit and download.

#### C) FDA 510(k) Intelligence / Review Pipeline
- Input device identifiers and context; generate intelligence memo; structure submission; apply checklist; generate review memo; chat/iterative refinement (preserved).

#### D) Note Keeper & Magics
- Paste notes → structured markdown (keywords in coral) → edit → apply AI Magics (6 features) (preserved and clarified in this spec).

---

## 3. Architecture & Components

### 3.1 Components

1. **Streamlit UI Layer**
   - Tabs: Dashboard, TW Premarket, 510(k) Intelligence, PDF→Markdown, 510(k) Review Pipeline, Note Keeper & Magics, Agents Config
   - Sidebar: global settings + API key handling + painter themes + default model parameters + agents.yaml upload

2. **Session State Store (in-memory)**
   - Canonical objects:
     - `settings`: theme/language/style/model/max_tokens/temperature
     - `api_keys`: provider keys (masked)
     - `tw_application`: structured TFDA application object (new consolidated structure)
     - `guidance_docs`: processed guidance markdown + metadata
     - `agent_runs`: outputs, edits, statuses, token estimates
     - `history`: dashboard activity

3. **LLM Gateway**
   - Provider routing by model id
   - Consistent interface: `(system_prompt, user_prompt, max_tokens, temperature, api_keys)`
   - Safety: never log keys; never persist them

4. **Document Processor**
   - PDF extraction (pypdf)
   - Optional vision-OCR via GPT/Gemini vision models (conceptual; implementation decisions kept minimal, but interface specified)
   - Markdown cleanup agent

5. **Agent Orchestrator**
   - Reads `agents.yaml`
   - Provides unified “Agent Runner UI” across modules with:
     - prompt override
     - model selection
     - `max_tokens` override
     - editable output as next input

---

## 4. WOW UI/UX (Required Enhancements)

### 4.1 Theme & Internationalization
**Must provide:**
- Light / Dark toggle
- English / Traditional Chinese toggle
- **20 painter styles** (as already listed) + **Jackpot** randomizer

**Design expectations:**
- Glassmorphism cards, gradient backgrounds tied to painter style
- Monospace for editors; sans-serif for UI
- High-contrast accessibility in both themes

### 4.2 WOW Status Indicators (System-wide)
Add persistent, visually strong status elements:
- **Step badges:** Pending / Running / Done / Error
- **Completion meters:** e.g., TFDA basic form completeness %
- **Run telemetry:** tokens estimate, model, timestamp
- **Dashboard “Status Wall”:** last run snapshot + heatmap + trends (already present; ensure TW form runs are included)

### 4.3 Interactive Dashboard (Preserve + Expand)
Dashboard continues to show:
- total runs, unique tabs, token sums
- runs by tab, runs by model
- tab×model heatmap
- token usage over time
- recent activity table

**Additional dashboard metrics (new):**
- TFDA application completeness trend (last N edits / run time snapshots)
- Count of missing required fields at last generation
- Number of attachments marked “適用/不適用/未判定”

---

## 5. API Key Handling (Required Behavior)

1. The system must check environment variables first:
   - `OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `GROK_API_KEY`

2. **If key exists in environment:**
   - Show “key from environment” caption
   - Do **not** display the key value or allow copy

3. **If missing in environment:**
   - Provide a password-masked input in sidebar
   - Store only in `st.session_state.api_keys` for the session
   - Never write to disk; never print to logs

---

## 6. Model & Agent Controls (Required Enhancements)

### 6.1 Model Catalog
Selectable models must include (exact list required):
- `gpt-4o-mini`
- `gpt-4.1-mini`
- `gemini-2.5-flash`
- `gemini-3-flash-preview`
- `gemini-2.5-flash-lite`
- `gemini-3-pro-preview`
- **anthropic models** (configurable set; at minimum keep existing Claude entries)
- `grok-4-fast-reasoning`
- `grok-3-mini`

**Note:** Provider routing must be deterministic and validated at runtime.

### 6.2 Per-Agent Preflight Editing (One-by-one execution)
Before running any agent, user must be able to:
- Edit agent prompt (user prompt)
- Select model
- Set `max_tokens` (default 12000)
- Execute agent and receive output
- Edit output in Markdown or plain text view
- Use edited output as the **input to the next agent**

**UI pattern:**
- `Input` pane
- `Prompt` pane
- `Model/max_tokens` selectors
- `Run` button with status indicator
- `Output` pane with Markdown/Text toggle
- `Use as Next Input` action (conceptual; implemented by copying edited output into the next agent’s input buffer)

---

## 7. New Module: TFDA Application Form – Basic Data (PDF-aligned)

### 7.1 Goal
Provide a structured fill-in experience matching the provided “申請填寫畫面-基本資料” content. This must be more than free-text: it should capture the core data model for downstream:
- Application markdown generation
- Completeness checking
- Screening agent review
- Export/import interoperability

### 7.2 Data Model (New/Updated TFDA Schema)

Create a canonical object `tw_application.basic_data` with these fields (Traditional Chinese labels shown; internal keys in English snake_case):

#### 7.2.1 Dates & Administrative
- `fill_date`（填表日, date)
- `received_date`（公文收文日, date)
- `device_type`（醫療器材: `一般醫材` | `體外診斷器材(IVD)`）
- `case_category`（案件種類: `新案` | `申復`）
- `case_type`（案件類型: at least `許可證變更`; extensible list）
- `license_scope`（許可證字號/分類分級品項, enum: `許可證號` | `分類分級品項`）

#### 7.2.2 License & Device Identity
- `license_number`（許可證號，例如「衛署醫器製字 第 003404 號」）
- `device_name_zh`（中文名稱）
- `device_name_en`（英文名稱）
- `risk_class`（風險等級: `第二等級` | `第三等級`）

#### 7.2.3 Classification (主分類 / 次分類 with operations)
A dynamic list `classifications[]` where each item:
- `main_category` (e.g., `A.臨床化學及臨床毒理學`)
- `sub_category_code` (e.g., `A.1225`)
- `sub_category_name` (e.g., `肌氨酸酐試驗系統`)
- `operation` (UI action: add/remove row)

**Requirement:** Support multiple rows; allow reorder; validate that sub-category matches the selected main category (soft validation via mapping table or LLM assist).

#### 7.2.4 Origin / Similarity / Substitution
- `origin`（產地: `國產` | `輸入` | `陸輸`）
- `has_similar_products`（有無類似品: `有` | `無` | `全球首創` | `非新增/變更規格`）
- `substitution`（替代: `是` | `否` | `非新增/變更規格`）

#### 7.2.5 Change Type Matrix (許可證變更)
A structured list `change_items[]`, each item contains:
- `change_item`（項目，例如：中文品名、英文品名、原廠標籤/說明書/包裝、成分材料結構規格型號變更(涉及/未涉及安全效能)…、效能用途適應症變更、變更製造業者名稱/地址/國別、變更許可證所有人/名稱、遺失補發、汙損換發、涉及商標變更、製造許可編號、其它）
- `original_approval`（原核准登記事項, free text）
- `requested_change`（申請變更事項, free text）
- Optional flags:
  - `involves_trademark_change` (bool)
  - `manufacturing_mode_original` / `manufacturing_mode_new` (enum: 單一製造廠 / 全部製程委託製造 / (O)/(P)製造)

**Requirement:** UI must present this as a table/grid similar to screenshot.

#### 7.2.6 Explanation
- `change_reason`（說明理由, multiline text)

### 7.3 Applicant (申請商資料) – Structured Fields
Within `tw_application.applicant`:
- `company_uniform_no`（統一編號）
- `company_name`（醫療器材商名稱）
- `company_address`（地址）
- `responsible_person`（負責人姓名）
- `contact_person`（聯絡人姓名）
- `contact_phone`（電話 + 分機）
- `contact_email`（電子郵件）

Also support “修正前” values:
- `previous_values` object mirroring the above keys (optional)
- UI shows “修正前” fields only when case type suggests change/rectification (toggle “顯示修正前資訊”).

### 7.4 Attachments / Document Checklist (From Screenshot Items)
Add `tw_application.attachments[]` with items representing the checklist sections shown, such as:
- 一、醫療器材許可證變更登記申請書（適用/不適用）
- 二、原核准文件（原許可證、騎縫章標籤/說明書/包裝）
- 四、變更說明文件（比較表、原廠變更說明函）
- 七、出產國製售證明
- 八、國外原廠授權登記書
- 九、QMS/QSD 證明文件
- 十、委託製造相關文件
- 十一、標籤/說明書/包裝擬稿（中文標籤、原廠標籤包裝、中文說明書擬稿、原廠型錄使用說明書、產品圖片等）
- 十二、產品結構材料規格性能用途圖樣資料
- 十四、產品特定安全性要求（動物組織、PVC/DEHP、著色劑等）
- 十七、臨床前測試及品質管制資料（電性安全 IEC60601-1、EMC IEC60601-1-2、生物相容性、滅菌、安定性、功能性測試、IVD性能、軟體確效 IEC62304、資安、重處理、MRI相容性等）
- 十八、臨床證據資料

Each attachment item contains:
- `section_id`, `section_title`
- `applicability` (enum: `適用` | `不適用` | `未判定`)
- `notes` (text)
- `files[]` metadata (filename, description, status such as 作廢/有效, optional)

**Requirement:** The UI must allow users to record “作廢” status per file line, reflecting screenshot patterns.

### 7.5 Form UX Requirements (Mirroring the PDF Screen)
- Present as “Basic Data” page with grouped blocks and red asterisk markers for required fields.
- Must include:
  - Date inputs (填表日 / 公文收文日)
  - Radio groups for device type / risk class / origin / similar / substitution
  - Selectboxes for case category/type
  - License number field and device name fields
  - Classification grid (主分類/次分類/操作)
  - Change type matrix table with rows pre-populated by common options (editable cells)
  - Applicant data section with optional “修正前” display
  - Attachment checklist section with applicability toggles and optional file list

### 7.6 Validation & Completeness Scoring
Define required fields for “Basic Data completeness” (example baseline):
- fill_date, received_date
- device_type
- case_category
- case_type
- license_number OR classification item (depending on `license_scope`)
- device_name_zh, device_name_en
- risk_class
- at least one `classifications[]` row
- origin
- applicant: uniform_no, company_name, company_address, responsible_person, contact_person, phone, email
- change_reason (required if case_type is 許可證變更)

Completeness algorithm:
- Weighted score:
  - Identity & dates (20%)
  - Classification (20%)
  - Applicant info (30%)
  - Change matrix + reason (30%)
- Show WOW card + progress bar and list of missing required fields.

### 7.7 Import/Export Interop (Preserve + Extend)
Keep existing JSON/CSV import/export, but extend mapping to new schema:
- Export:
  - `tw_application.json` canonical (recommended)
  - Flattened CSV for basic fields + separate CSV for classifications/change_items/attachments (or a single JSON as primary)
- Import:
  - Accept arbitrary JSON/CSV and normalize into canonical schema via LLM standardizer (Gemini default, but user-selectable)

### 7.8 OCR-assisted Auto-fill (Optional but Strongly Recommended)
To align with “based on attached pdf/screenshots,” add a workflow:
- User uploads:
  - PDF or images (screenshots)
- System extracts text:
  - PDF text extraction (pypdf) for digital PDFs
  - LLM vision OCR for scanned/graphics-heavy pages
- Normalization agent maps extracted content into `tw_application` schema.

**Constraints:**
- Do not hallucinate missing fields; mark unknown as empty and list uncertainties.

---

## 8. Application Markdown Generation (Updated)
When user clicks “Generate Application Markdown Draft,” output should:
1. Render a **Basic Data summary** section with:
   - Dates, device type, case category/type
   - License number and device names
   - Risk class and origin
2. Render **Classification table** (主分類/次分類代碼/名稱)
3. Render **Change matrix** table (項目/原核准/申請變更)
4. Render **Applicant data** (and “修正前” if present)
5. Render **Attachments checklist** as a table with applicability + file list references
6. Include “※待補” markers when required fields are missing.

The generated markdown remains editable in Markdown/Text view, synchronized by “Apply changes” pattern (pragmatic sync acceptable).

---

## 9. TFDA Screening Agent (Enhanced Inputs)
The TW Screen Review Agent must receive combined input:
- Application markdown draft (including the new basic data sections)
- Guidance text/markdown (uploaded or pasted)
- Optional: extracted OCR text from attachments list sections (if available)

The output remains:
- completeness matrix
- missing/ambiguous items
- action items grouped into “必須補件” and “建議補充”
- explicit “依現有輸入無法判斷” markers

---

## 10. Note Keeper (Preserve + Strengthen)
### 10.1 Baseline Flow (Preserved)
- Paste note (text/markdown)
- Agent transforms into organized markdown with keywords highlighted in coral (system may suggest keywords; user can override)
- User edits note in Markdown or text view

### 10.2 AI Magics: 6 Features (Required)
Keep existing and formalize into 6 clearly defined tools:

1. **AI Formatting**: normalize headings/lists without changing meaning  
2. **AI Keywords**: user provides keywords + color; system highlights in rendered markdown (coral default)  
3. **AI Summary**: bullet summary + short narrative  
4. **AI Action Items**: table of tasks, owners (optional), priority, notes  
5. **AI Glossary**: term table (EN/中文/解釋)  
6. **AI Risk Flags** (new): detect regulatory risk statements (e.g., missing evidence, inconsistent claims) and produce a “Risk Register” table with severity/likelihood and suggested mitigations

All Magics must be model-selectable and prompt-editable.

---

## 11. Configuration Management (Preserved)
### 11.1 `agents.yaml`
- View/edit raw YAML
- Upload/download
- Validate schema:
  - `name`, `model`, `temperature`, `max_tokens`, `system_prompt`, `user_prompt_template` (recommended)
- If invalid: run “Config Standardizer” agent to repair structure (as described in earlier spec)

### 11.2 `SKILL.md`
- View/edit/upload/download
- Used as optional shared instruction set for multiple agents (future extension)

---

## 12. Non-Functional Requirements

### 12.1 Security & Privacy
- API keys never persisted
- No PII logging
- Provide “Clear session” control (recommended) to wipe in-memory data
- Download exports happen client-side via Streamlit download button

### 12.2 Reliability
- Provider timeouts and user-facing error messages
- Status indicator transitions: pending → running → done/error
- Preserve last successful outputs even if next run fails

### 12.3 Performance
- Favor incremental extraction (page trimming)
- Keep OCR optional due to cost/latency
- Token estimation is approximate; provide warnings when user selects high max_tokens

### 12.4 Accessibility
- Contrast-safe palette in light/dark themes
- Keyboard-friendly navigation within forms
- Clear required-field markers and inline validation feedback

---

## 13. Deployment on Hugging Face Spaces (Streamlit)
- `requirements.txt` must include:
  - streamlit, pandas, pypdf, pyyaml
  - openai, google-generativeai, anthropic, httpx
  - altair
  - optional: reportlab, python-docx
- Secrets configured in HF Space settings:
  - OPENAI_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY, GROK_API_KEY

---

## 14. Acceptance Criteria (Must Pass)

1. User can complete TFDA **Basic Data** form aligned to provided screenshot fields.
2. User can add multiple classification rows (主分類/次分類).
3. User can fill change matrix (原核准 vs 申請變更) and generate markdown reflecting it.
4. Attachments checklist supports “適用/不適用/未判定” and optional file rows with “作廢” marking.
5. Completeness % updates and missing fields are listed.
6. User can run TW Screen Review agent with editable prompt/model/max_tokens.
7. Output is editable and can be used as input for subsequent agents.
8. WOW UI supports theme + language + 20 painter styles + Jackpot.
9. API key behavior matches requirements (environment key not displayed; UI input if missing).
10. Dashboard shows activity across all modules.

---

# 20 Comprehensive Follow-up Questions

1. In the TFDA “案件種類” field, do you want the allowed values strictly limited to `新案/申復`, or must we support additional states (e.g., `展延案`, `變更案`) depending on other workflows?
2. For “案件類型,” should the UI provide a fixed enumeration (e.g., 許可證變更 / 查驗登記新案 / 展延), or allow free-text with suggestions?
3. The screenshot shows both “許可證字號/分類分級品項” — should the user select one mode, or can both be captured simultaneously?
4. For the classification list (主分類/次分類), do you require a full offline taxonomy table embedded in the app, or is LLM-assisted mapping acceptable for validating sub-category options?
5. Should the “次分類” dropdown be dynamically filtered based on “主分類” selection (recommended), even if it increases UI complexity?
6. For “風險等級,” should the system enforce that IVD devices can still be class II/III only, or allow class I for future expansion?
7. For “產地,” do you want “輸入” to require manufacturer country/address fields immediately (hard validation), or only as a later completeness warning?
8. In the “變更種類” matrix, should rows be pre-populated with the full list shown (long), or only the most common items with an “Add row” option?
9. Do you need the matrix to support attachments per change item (e.g., linking a “比較表” file specifically to “型號變更”)?
10. For “修正前” values in applicant info, should the system store them as a versioned history (multiple previous states), or only a single “previous” snapshot?
11. Should the Basic Data page support “auto-fill from last application” templates to speed up repeat submissions for the same company/device?
12. For the attachments checklist, do you want the checklist items to be configurable via `agents.yaml`/`SKILL.md` (so different device classes load different checklists)?
13. The screenshot includes many “不適用/適用” toggles—should the app enforce dependencies (e.g., if 委託製造=不適用 then hide 委託製造文件 section)?
14. For file metadata rows (檔案名稱/檔案說明/註銷 作廢), do you need actual file upload storage, or is metadata-only tracking sufficient for now?
15. If actual uploads are required, should files persist across sessions (HF storage) or remain session-only (recommended for privacy)?
16. For OCR-assisted auto-fill, do you want the user to upload the original PDF, or is screenshot image upload sufficient as a primary workflow?
17. When OCR/LLM cannot confidently extract a field (e.g., license number), should the system leave it blank only, or also generate a “疑似值” with confidence score?
18. For bilingual UI, should field labels always follow the chosen language, or show bilingual labels simultaneously for regulatory clarity?
19. Do you want a dedicated “Application Form Preview” that visually mimics the government portal layout (table-like), or is a structured Streamlit form acceptable as long as fields match?
20. Should the TW Screen Review agent output be aligned to a specific internal template (company SOP), such as mandatory headings, risk grading, and standardized action-item numbering?
