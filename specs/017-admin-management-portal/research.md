# Research: Admin Management Portal

## Decisions

### 1. 管理員跳轉邏輯 (Login Redirection)
- **Decision**: 在前端 `LoginView.vue` 處理登入成功後的邏輯。如果 `authStore.user?.role === 'admin'`，導向 `/admin/dashboard`；否則導向 `route.query.redirect` 或 `/`。
- **Rationale**: 讓跳轉邏輯集中在前端，使用者體驗更流暢。後端 API 回傳的 User 物件已包含 `role` 資訊。
- **Alternatives considered**: 由後端回傳跳轉網址（過度設計，前端應掌控路由）。

### 2. 後台 Layout 設計 (Admin Layout Design)
- **Decision**: 建立一個 `AdminLayout.vue`，採用「左側固定導覽列 + 右側內容區」的標準後台佈局。
- **Rationale**: 側邊欄適合容納多個管理功能（商品管理、訂單管理等），並提供清晰的功能導覽。
- **UI Components**: 使用 `Lucide` 圖示與 `shadcn/ui` 風格保持一致。

### 3. 「查看前台」與「返回後台」功能 (Public/Admin Switcher)
- **Decision**: 
    - **前台 -> 後台**: 在全域 `Navbar.vue` 中判斷使用者是否為管理員，若是則在使用者選單或頂端顯示「管理後台」按鈕。
    - **後台 -> 前台**: 在 `AdminLayout.vue` 的側邊欄下方提供「查看前台」連結。
- **Rationale**: 提供雙向快捷入口，方便管理員隨時切換環境。

### 4. 路由保護與 RBAC (Role-Based Access Control)
- **Decision**: 在 `frontend/src/router/index.ts` 的 `beforeEach` 守衛中，針對所有 `meta.requiresAdmin` 的路徑檢查 `user.role`。
- **Rationale**: 確保普通使用者即使手動輸入網址也無法進入後台。

## Research Tasks

- [x] 確認登入成功後，`authStore` 是否能即時更新 `user.role` -> 已在 016 功能中實作。
- [x] 設計 `AdminLayout.vue` 的響應式側邊欄。
- [x] 確定管理員預設首頁的路徑為 `/admin/dashboard`。
