<!--
Sync Impact Report:
- Version change: 0.0.0 (Template) -> 1.0.0
- Principles Defined:
  - 高品質 (High Quality)
  - 可測試性 (Testability)
  - MVP 優先 (MVP First)
  - 避免過度設計 (Avoid Overdesign)
  - 正體中文優先 (Traditional Chinese First)
- Templates checked: 
  - plan-template.md (✅ Compatible)
  - spec-template.md (✅ Compatible)
  - tasks-template.md (✅ Compatible)
  - checklist-template.md (✅ Compatible)
-->

# cy-ecommerce-web Constitution

## Core Principles

### I. 高品質 (High Quality)
代碼必須具備高品質，嚴格遵循最佳實踐。我們追求強健、清晰且易於維護的代碼庫，不因趕工而犧牲品質。每一次提交都應代表著我們對卓越工程的承諾。

### II. 可測試性 (Testability)
系統必須設計為可測試的 (Testable)。測試代碼與產品代碼同等重要，它是我們信心的來源。透過單元測試、整合測試等手段，確保功能的正確性，並防止未來的變更破壞現有功能。

### III. 最小可行性產品 (MVP First)
專注於開發最小可行性產品 (Minimum Viable Product)。優先識別並交付能帶來核心價值的最少功能集。避免功能蔓延 (Feature Creep)，確保能夠快速迭代並從使用者反饋中學習。

### IV. 避免過度設計 (Avoid Overdesign)
拒絕過度設計。遵循 KISS (Keep It Simple, Stupid) 與 YAGNI (You Aren't Gonna Need It) 原則。不要為了解決「未來可能發生」的問題而引入不必要的複雜度；解決當前的問題，並保持架構的簡單與彈性。

### V. 正體中文優先 (Traditional Chinese First)
本專案中所有的文檔、代碼註釋、架構設計說明以及溝通內容，一律使用正體中文。這確保了團隊溝通的精確性與一致性。

## 技術與開發約束

### 技術棧
- **主要語言**: Python (後端/腳本)
- **開發環境**: 遵循 Docker 化或虛擬環境標準，確保環境一致性。**開發環境中不需要執行 alembic migration**，系統啟動時會自動處理資料表結構同步（透過 `recreate_all`）。

### 質量保證
- 所有功能開發必須包含相應的測試用例。
- 提交前必須通過 linting 與格式化檢查。

## 開發流程

### 迭代開發
- 採用敏捷開發思維，以小步快跑的方式推進。
- 每個功能開發前需進行規格確認 (Spec) 與計畫 (Plan)。

### 審查機制
- 所有代碼變更需經過 Code Review。
- 確保變更符合本憲法所列之原則。

## Governance

本憲法是專案的最高指導原則，優先於其他慣例。

### 修訂程序
- 任何對原則的修改都需要經過團隊討論與記錄。
- 修訂必須更新版本號與修訂日期。
- 重大變更 (Major) 需有遷移計畫。

**Version**: 1.0.0 | **Ratified**: 2025-12-03 | **Last Amended**: 2025-12-03