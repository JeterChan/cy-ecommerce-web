# Quickstart: Admin Management Portal

## 核心流程驗證

### 1. 管理員登入跳轉
- **帳號**: `admin@test.com` / `Admin123!` (需先執行 `seed_admin.py`)。
- **步驟**: 在 `/login` 頁面登入。
- **預期**: 登入成功後應自動跳轉至 `/admin/dashboard`。

### 2. 前後台切換
- **後台 -> 前台**: 點擊側邊欄底部的「查看前台」。
- **前台 -> 後台**: 管理員登入狀態下，點擊頂端導覽列的使用者選單中的「管理後台」。

### 3. 路由保護
- **測試**: 以普通使用者 (`role: user`) 登入，手動輸入 `/admin/dashboard`。
- **預期**: 應被導回首頁或顯示錯誤。

## 開發除錯
- **Vue Router**: 檢查 `frontend/src/router/index.ts` 中的 `beforeEach`。
- **Layout**: 核心組件位於 `frontend/src/layouts/AdminLayout.vue`。
