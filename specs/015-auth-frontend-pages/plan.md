# 技術實作計畫：驗證系統前端頁面擴展 (Auth Frontend Pages Extension)

**功能分支**: `015-auth-frontend-pages`  
**建立日期**: 2026-03-11  
**狀態**: 規劃中 (Planning)  
**關聯規格**: [spec.md](./spec.md)

## 技術背景 (Technical Context)

### 前端技術棧 (Confirmed)
- **Framework**: Vue 3.5+ (Composition API)
- **Styling**: Tailwind CSS 3.4+ / shadcn-vue (radix-vue)
- **State**: Pinia 3.0+
- **Form**: vee-validate / zod
- **API**: Axios 1.13+
- **Language**: TypeScript 5.9+

### 技術約束 (Technical Constraints)
- **語言限制**: 僅限正體中文 (Traditional Chinese)。
- **架構原則**: 遵循憲法 principles (高品質, 可測試性, MVP)。
- **API 整合**: 需串接後端 `email-verify`, `forgot-password`, `reset-password` API。

## 憲法檢查 (Constitution Check)

- **高品質 (High Quality)**: 使用 TypeScript 嚴格定義型別與 API 合約。
- **可測試性 (Testability)**: 為每個新表單元件撰寫單元測試 (`vitest`)。
- **MVP 優先 (MVP First)**: 先實現核心驗證與編輯流程，暫不開發複雜的頭像裁切。
- **正體中文優先 (Traditional Chinese First)**: UI 與代碼註釋全面使用正體中文。

## 實作階段 (Implementation Phases)

### 階段 1: 基礎架構與 API 封裝
- 更新 `src/services/auth.service.ts` 增加忘記密碼與驗證方法。
- 更新 `src/i18n/locales/zh-TW.json` 加入新字串。
- 定義 Zod 驗證 Schema 於 `src/models/auth.schema.ts`。

### 階段 2: UI 元件開發
- 開發 `ForgotPasswordForm.vue`。
- 開發 `ResetPasswordForm.vue`。
- 開發 `ProfileEditForm.vue` (包含刪除帳號二次確認)。

### 階段 3: 路由與 View 整合
- 建立 `views/auth/ForgotPasswordView.vue`。
- 建立 `views/auth/ResetPasswordView.vue`。
- 建立 `views/auth/VerifyEmailView.vue` (處理 Token 並自動呼叫 API)。
- 更新 `views/ProfileView.vue`。
- 在 `router/index.ts` 配置相對應的路由與導航守衛。

### 階段 4: 測試與驗證
- 撰寫表單驗證與 API 呼叫的單元測試。
- 執行端對端手動測試 (E2E Manual Testing)。
- 執行 linting 與型別檢查。

## 生成產物 (Generated Artifacts)
- `research.md`: 決策紀錄。
- `data-model.md`: 前端實體與驗證規則。
- `quickstart.md`: 開發環境啟動指南。
- `contracts/`: API 交換合約 (待補足 OpenAPI 定義)。

## 簽署與確認
- [x] 符合專案架構
- [x] 符合憲法原則
- [x] 已獲得使用者初步技術確認
