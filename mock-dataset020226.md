## 3 Mock Application Datasets（繁中 / JSON）

> 下列三套皆為「虛構示例資料」，可直接另存為 `mock_app_*.json`，或貼到系統的 import 功能中使用。

### Mock Dataset 1：血糖測試儀許可證變更（對應你貼的案例）
```json
{
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
    "change_reason": "本次變更涉及中文/英文品名與標籤/說明書更新，並修訂部分規格文字敘述；產品技術原理不變。"
  },
  "classifications": [
    {
      "main_category": "A.臨床化學及臨床毒理學",
      "sub_category_code": "A.1345",
      "sub_category_name": "葡萄糖試驗系統"
    },
    {
      "main_category": "J.一般醫院及個人使用裝置",
      "sub_category_code": "J.9999",
      "sub_category_name": "其他（自我監測用血糖測試儀）"
    }
  ],
  "change_items": [
    {
      "change_item": "中文品名",
      "original_approval": "欣活語音血糖測試儀",
      "requested_change": "欣活語音血糖測試儀（新版包裝）"
    },
    {
      "change_item": "英文品名",
      "original_approval": "GlucoSure VIVO Blood Glucose Meter",
      "requested_change": "GlucoSure VIVO Voice Blood Glucose Meter"
    }
  ],
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
      "responsible_person": "沈燕士"
    }
  },
  "attachments": [
    {
      "section_id": "1",
      "section_title": "一、醫療器材許可證變更登記申請書",
      "applicability": "適用",
      "notes": "已準備",
      "files": [
        { "file_name": "變更登記申請書.pdf", "status": "有效" }
      ]
    }
  ]
}
```

### Mock Dataset 2：第三等級骨科植入物新案
```json
{
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
    "change_reason": "不適用（新案）"
  },
  "classifications": [
    {
      "main_category": "N.骨科學",
      "sub_category_code": "N.9999",
      "sub_category_name": "其他（脊椎植入物）"
    }
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
    {
      "section_id": "11",
      "section_title": "十一、標籤、說明書或包裝擬稿",
      "applicability": "適用",
      "notes": "含中文標籤、UDI、使用方式與禁忌",
      "files": [
        { "file_name": "中文說明書_v1.pdf", "status": "有效" }
      ]
    }
  ]
}
```

### Mock Dataset 3：連網居家生理量測系統（軟體/資安變更）
```json
{
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
    "change_reason": "本次變更新增行動 App 之資安機制（帳號鎖定/加密傳輸）及修訂說明書資安警語；量測硬體不變。"
  },
  "classifications": [
    {
      "main_category": "J.一般醫院及個人使用裝置",
      "sub_category_code": "J.9999",
      "sub_category_name": "其他（居家量測/遠距傳輸）"
    }
  ],
  "change_items": [
    {
      "change_item": "原廠標籤、說明書或包裝",
      "original_approval": "說明書 v1.0",
      "requested_change": "說明書 v1.1（新增資安警語與帳號管理說明）"
    },
    {
      "change_item": "成分、材料、結構、規格或型號變更（涉及安全及效能評估）",
      "original_approval": "App 未提供帳號鎖定",
      "requested_change": "App 新增帳號鎖定與TLS傳輸，新增資安測試摘要"
    }
  ],
  "applicant": {
    "company_uniform_no": "11223344",
    "company_name": "康雲智慧醫療股份有限公司",
    "company_address": "台中市西屯區市政北二路 66 號 8F",
    "responsible_person": "許文豪",
    "contact_person": "陳怡君",
    "contact_phone": "04-2258-1234 分機 206",
    "contact_email": "qa-ra@healthcloud.tw",
    "previous_values": {
      "company_uniform_no": "11223344",
      "company_name": "康雲智慧醫療股份有限公司",
      "company_address": "台中市西屯區市政北二路 66 號 8F",
      "responsible_person": "許文豪"
    }
  }
}
```

---

## 3 Mock Review Guidance（繁中 / Markdown）

### Guidance 1：許可證變更—形式審查指引（對應 Dataset 1）
```markdown
# TFDA 形式審查/預審指引（範例1：許可證變更）

## 一、基本資料完整性
- 「填表日」「公文收文日」必填，日期格式一致（YYYY-MM-DD）。
- 「醫療器材類型」「案件種類」「案件類型」「產地」「風險等級」必填。
- 若為「許可證變更」，必須提供：
  - 許可證號（完整字號）
  - 變更種類矩陣（至少 1 項有具體內容）
  - 說明理由（含是否影響安全/效能）

## 二、文件附件一致性
- 變更登記申請書：通常必附（遺失補發/汙損換發另行判定）。
- 原核准文件：若涉及標籤/說明書/包裝，通常必附原核准版本。
- 變更說明文件：應附「變更比較表」與（如適用）「原廠變更說明函」。
- QMS/QSD：如勾選適用，應附有效證明並可追溯製造廠與產品範圍。

## 三、常見缺漏
- 變更理由僅寫「更新」但未說明更新點 → 可能不足
- 變更涉及規格/軟體/性能，但無風險評估或佐證 → 明顯缺漏
- 附件勾選適用但未列檔，或檔案作廢無替代 → 缺漏
```

### Guidance 2：第三等級骨科植入物新案—技術/臨床重點（對應 Dataset 2）
```markdown
# TFDA 審查重點指引（範例2：第三等級骨科植入物新案）

## 必備文件
1. 中文標籤/說明書擬稿（適應症、禁忌、警語、保存/滅菌資訊如適用）。
2. 技術檔案：結構、材料、規格、製程、圖樣、性能。
3. 風險管理：ISO 14971 架構（危害分析、風險控制、殘餘風險可接受性）。
4. 生物相容性：依接觸性質/時間提供 ISO 10993 相關評估/試驗。
5. 臨床證據：第三等級需充分；若採文獻應說明可比性與等同性。

## 常見缺漏
- 僅宣告符合但無測試摘要/判讀 → 可能不足
- 材料來源/表面處理未說明 → 明顯缺漏
- 說明書與技術檔案不一致（規格/適應症）→ 需釐清
```

### Guidance 3：連網/軟體變更—資安與V&V（對應 Dataset 3）
```markdown
# TFDA 審查指引（範例3：連網/軟體變更）

## 變更必要說明
- 變更範圍、變更原因、是否影響安全/效能需寫清楚。
- 若涉及軟體/連網功能，至少應提供：
  - 版本/修訂歷史（Revision Level History）
  - 風險分析（含資安風險）
  - 查證與確認（V&V）摘要
  - 追溯性（需求→測試）說明或摘要

## 資安最低期待
- 資料流與加密策略
- 身分驗證與存取控制
- 弱點管理與更新機制（含 OTA/更新流程）

## 常見缺漏
- 僅寫「新增加密」但無範圍與測試 → 可能不足
- 缺乏追溯性 → 明顯缺漏
- 說明書未更新資安警語 → 需補充
```
