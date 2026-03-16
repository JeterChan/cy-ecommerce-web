# Data Model: Admin Management Portal

## Entities

### User (現有)
使用者實體包含角色欄位，用於決定存取權限。

- **role**: 字串
    - `admin`: 可存取 `/admin/*` 路由及相關 API。
    - `user`: 僅能存取前台功能。

## Validation Rules

- **RBAC 驗證**: 所有以 `/api/v1/admin/` 為前綴的後端 API 必須驗證 Token 中的使用者角色是否為 `admin`。
- **前端導航守衛**: 具備 `requiresAdmin: true` 標記的路由，必須檢查 `authStore.user.role`。
