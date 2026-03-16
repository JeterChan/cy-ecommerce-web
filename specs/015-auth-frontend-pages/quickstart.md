# 快速開始：驗證系統前端頁面擴展 (Auth Frontend Pages Extension)

## 環境設置 (Environment Setup)

1. 確認後端 API 已啟動 (預設: `http://localhost:8000`)。
2. 進入前端目錄: `cd frontend`
3. 安裝依賴: `npm install`
4. 啟動開發伺服器: `npm run dev`

## 主要路由說明 (Main Routes)

- `/auth/forgot-password`: 忘記密碼頁面。
- `/auth/reset-password`: 重設密碼頁面 (需附帶 `?token=...`)。
- `/auth/verify-email`: 信箱驗證落地頁面 (需附帶 `?token=...`)。
- `/profile`: 個人檔案編輯與管理頁面 (需登入)。

## 開發任務重點 (Development Focus)

1. **i18n 配置**: 確保 `src/i18n/locales/zh-TW.json` 已包含所有新元件的文字描述。
2. **API Service**: 更新 `src/services/auth.service.ts` 處理忘記密碼與驗證請求。
3. **UI 元件**: 使用 `radix-vue` 與 `shadcn/ui` 風格構建表單。
4. **驗證流程**: 確保 `email-verify` 在 `mounted` 時觸發並正確處理 Token。
