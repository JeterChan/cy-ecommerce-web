# 研究與決策：驗證系統前端頁面擴展 (Auth Frontend Pages Extension)

## 技術背景與決策 (Decisions & Rationale)

### 1. 組件組織方式 (Component Organization)
- **決策**: 
  - 認證相關的頁面放置於 `frontend/src/views/auth/`。
  - 重用性高的認證元件（如 ForgotPasswordForm, ResetPasswordForm）放置於 `frontend/src/components/auth/`。
- **理由**: 符合專案現有的 `views` 與 `components` 分離架構，並將認證模組獨立分類以利維護。

### 2. API 端點確認 (API Endpoints)
- **決策**: 
  - 忘記密碼: `POST /api/v1/auth/forgot-password`
  - 重設密碼: `POST /api/v1/auth/reset-password`
  - 個人資料: `GET /api/v1/users/me`, `PATCH /api/v1/users/me`
  - 帳號刪除: `DELETE /api/v1/users/me`
  - 信箱驗證: `GET /api/v1/auth/email-verify?token={token}`
- **理由**: 參考後端 FastAPI 的常見命名慣例，並預留 `v1` 版本路徑。
- **待確認**: 實際後端 `auth` 模組的精確路徑需在實作時與 `services/auth.service.ts` 對接。

### 3. 表單驗證策略 (Form Validation Strategy)
- **決策**: 使用 `vee-validate` 配合 `zod` 定義 schema。
- **理由**: 這是專案現有的標準做法（參考 `package.json`），可確保驗證邏輯與型別安全一致。

### 4. 國際化 (Internationalization)
- **決策**: 所有的 UI 字串定義於 `frontend/src/i18n/locales/zh-TW.json`。
- **理由**: 符合「正體中文優先」原則，並使用 `vue-i18n` 管理多國語系，便於未來擴充。

## 替代方案評估 (Alternatives Considered)

- **內聯驗證邏輯**: 考慮過直接在組件內撰寫驗證，但為了保持代碼整潔與高品質，決定沿用 `zod` schema。
- **直接在 View 處理 API**: 考慮過在 View 內直接調用 Axios，但為了符合「高品質」原則，決定透過 `services/` 層封裝。

## 待解決事項 (Pending Actions)
- [ ] 確認後端是否已完成 `email-verify` 與 `forgot-password` API。
- [ ] 確認個人檔案編輯是否需要處理頭像上傳（本次計畫暫不包含，僅限資料編輯）。
