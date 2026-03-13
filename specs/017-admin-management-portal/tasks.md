# Tasks: Admin Management Portal

**Feature**: Admin Management Portal
**Status**: Complete
**Branch**: `017-admin-management-portal`

## Implementation Strategy
本功能採 Incremental Delivery 策略，先建立基礎佈局與儀表板頁面，再實作關鍵的跳轉邏輯與路由保護。
1. **佈局基礎**: 建立 `AdminLayout` 與 `AdminDashboard`。
2. **跳轉邏輯 (US1)**: 修改 `LoginView` 與路由守衛實作自動身分偵測與跳轉。
3. **前後台導航 (US2/US3)**: 在 Layout 中整合「查看前台」與「商品管理」等功能。

## Phase 1: Setup
- [x] T001 [P] 建立管理員視圖與佈局目錄 `frontend/src/views/admin/` 與 `frontend/src/layouts/`

## Phase 2: Foundational
- [x] T002 [P] 實作後台統一佈局組件 `frontend/src/layouts/AdminLayout.vue`（包含側邊欄結構）
- [x] T003 [P] 實作管理員儀表板首頁 `frontend/src/views/admin/AdminDashboard.vue` (包含歡迎語與快速連結 Mockup)

## Phase 3: User Story 1 - Automatic Admin Redirection (Priority: P1)
**Goal**: 管理員登入後自動導向後台入口頁。
**Independent Test**: 以 `admin@test.com` 登入後，自動抵達 `/admin/dashboard` 而非首頁。

- [x] T004 修改 `frontend/src/views/LoginView.vue` 加入基於 `role` 的跳轉邏輯
- [x] T005 更新 `frontend/src/router/index.ts` 註冊管理員路由並實作 `requiresAdmin` 導航守衛 (需處理 `redirect` 參數驗證)

## Phase 4: User Story 2 - Navigation to Public Store (Priority: P1)
**Goal**: 提供管理員在後台工作時快速查看前台的能力.
**Independent Test**: 在後台側邊欄點擊「查看前台」成功回到商城首頁。

- [x] T006 [P] [US2] 在 `frontend/src/layouts/AdminLayout.vue` 側邊欄加入「查看前台」連結
- [x] T007 [P] [US2] 更新 `frontend/src/components/layout/Navbar.vue` 為已登入管理員顯示「管理後台」入口

## Phase 5: User Story 3 - Admin Product Management Entry (Priority: P2)
**Goal**: 將現有的商品管理頁面整合進後台門戶.
**Independent Test**: 從管理員側邊欄點擊「商品管理」可進入商品 CRUD 介面。

- [x] T008 [US3] 在 `frontend/src/layouts/AdminLayout.vue` 側邊欄加入「商品管理」導覽項目

## Phase 6: Polish
- [x] T009 驗證不同角色 (Admin vs User) 的跳轉路徑與路由權限隔離 (包含登入過期後導回原頁面的 `redirect` 邏輯)
- [x] T010 調整 `AdminLayout` 在行動版裝置上的響應式顯示效果

## Dependencies
1. **Phase 2** (Foundational) 必須在 **Phase 3** (User Story 1) 之前完成，以確保跳轉目標存在。
2. **Phase 3** 完成後，管理員即可正常存取後台框架。

## Parallel Execution Examples
- **前端佈局設計**: T002 與 T003 可由同一人同時進行。
- **導覽元件更新**: T006 與 T007 可並行實作。
