# 開發任務清單：驗證系統前端頁面擴展 (Auth Frontend Pages Extension)

**功能名稱**: Auth Frontend Pages Extension
**實作計畫**: [plan.md](./plan.md)
**規格文件**: [spec.md](./spec.md)

## 實作策略
- **MVP 優先**: 優先實作核心的密碼重設與信箱驗證功能。
- **正體中文**: 所有的 UI 文字與錯誤提示必須使用 `src/i18n/locales/zh-TW.json`。
- **獨立測試**: 每個使用者情境 (User Story) 必須能夠獨立完成與驗證。

## 依賴圖 (Story Dependencies)
- Phase 1 & 2 (基礎建設) -> US1, US2, US3
- US2 (個人檔案) -> US4 (帳號刪除)

---

## Phase 1: 基礎建設 (Setup)
*目標: 初始化專案結構與多國語系配置*

- [x] T001 [P] 更新多國語系檔 `frontend/src/i18n/locales/zh-TW.json` 加入認證與個人檔案相關文字
- [x] T002 [P] 建立認證相關的 Zod 驗證 Schema 於 `frontend/src/models/auth.schema.ts`
- [x] T003 [P] 建立使用者資料的 TypeScript 介面於 `frontend/src/types/user.ts`

## Phase 2: 基礎功能 (Foundational)
*目標: 封裝 API 呼叫與建立共用元件*

- [x] T004 更新 `frontend/src/services/auth.service.ts` 加入 `forgotPassword`, `resetPassword`, `verifyEmail` 方法 (需包含 Axios 攔截器或 Try-Catch 錯誤處理與正體中文提示)
- [x] T005 更新 `frontend/src/services/user.service.ts` 加入 `getProfile`, `updateProfile`, `deleteAccount` 方法 (需實作網路中斷與授權失敗的異常處理)
- [x] T006 [P] 建立通用的二次確認對話框元件 (若尚未存在) 於 `frontend/src/components/ui/ConfirmDialog.vue`

---

## Phase 3: 使用者情境 1 - 忘記與重設密碼 (US1)
*目標: 實作完整的密碼找回流程*
*獨立驗證: 進入 /auth/forgot-password 輸入信箱後顯示成功訊息；點擊帶 Token 連結進入 /auth/reset-password 成功修改密碼*

- [x] T007 [P] [US1] 實作 `frontend/src/components/auth/ForgotPasswordForm.vue` 元件
- [x] T008 [P] [US1] 實作 `frontend/src/components/auth/ResetPasswordForm.vue` 元件
- [x] T009 [US1] 建立 `frontend/src/views/auth/ForgotPasswordView.vue` 並掛載元件
- [x] T010 [US1] 建立 `frontend/src/views/auth/ResetPasswordView.vue` 並掛載元件
- [x] T011 [US1] 在 `frontend/src/router/index.ts` 配置忘記與重設密碼路由
- [x] T012 [P] [US1] 為密碼重設表單撰寫單元測試於 `frontend/tests/components/auth/ResetPasswordForm.test.ts`

---

## Phase 4: 使用者情境 3 - 電子郵件驗證 (US3)
*目標: 實作註冊後的信箱啟用頁面*
*獨立驗證: 訪問 /auth/verify-email?token=xxx 頁面應自動呼叫 API 並顯示驗證結果*

- [x] T013 [US3] 建立 `frontend/src/views/auth/VerifyEmailView.vue` 落地頁面
- [x] T014 [US3] 在 `VerifyEmailView.vue` 的 `onMounted` 鈎子中實作 Token 提取與 API 調用邏輯
- [x] T015 [US3] 在 `frontend/src/router/index.ts` 配置信箱驗證路由
- [x] T015b [P] [US3] 撰寫 `VerifyEmailView.vue` 單元測試於 `frontend/tests/views/auth/VerifyEmailView.test.ts` (需模擬 API 成功/失敗情境)

---

## Phase 5: 使用者情境 2 - 個人檔案編輯與管理 (US2)
*目標: 提供登入使用者編輯個人資料的介面*
*獨立驗證: 在 /profile 頁面修改資料並儲存後，重新整理頁面確認資料已更新*

- [x] T016 [P] [US2] 實作 `frontend/src/components/profile/ProfileEditForm.vue` 元件
- [x] T017 [US2] 更新 `frontend/src/views/ProfileView.vue` 以整合編輯表單與顯示使用者資料
- [x] T018 [P] [US2] 為個人資料編輯撰寫單元測試於 `frontend/tests/components/profile/ProfileEditForm.test.ts`

---

## Phase 6: 使用者情境 4 - 帳號刪除 (US4)
*目標: 提供安全刪除帳號的功能*
*獨立驗證: 點擊刪除按鈕後彈出對話框，確認後成功刪除並被引導至登入頁面*

- [x] T019 [US4] 在 `ProfileEditForm.vue` 中加入「刪除帳號」按鈕與觸發確認邏輯
- [x] T020 [US4] 實作刪除成功後的清理 (Token 移除、Pinia Store 重置) 與重定向邏輯

---

## Phase 7: 磨光與跨功能關注點 (Polish)
*目標: 確保整體一致性與品質*

- [x] T021 [P] 檢查所有錯誤訊息是否皆為正體中文且符合 `zh-TW.json`
- [x] T022 [P] 執行 `npm run lint` 與 `vue-tsc` 確保無程式碼品質問題
- [x] T023 執行完整的人工冒煙測試，模擬用戶從忘記密碼到重設的完整路徑
- [x] T023b [P] 驗證系統效能符合規格書指標 (SC-001: 30秒內完成流程; SC-002: 3秒內顯示驗證結果)
