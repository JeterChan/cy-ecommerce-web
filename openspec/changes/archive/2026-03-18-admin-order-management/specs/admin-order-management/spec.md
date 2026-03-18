## ADDED Requirements

### Requirement: 管理員訂單分頁列表
系統 **MUST** 提供 API 端點 `/api/v1/admin/orders`，允許具備管理員權限的用戶獲取所有訂單的分頁列表。

#### Scenario: 成功獲取訂單列表
- **WHEN** 管理員請求 `/api/v1/admin/orders?page=1&limit=10`
- **THEN** 系統返回包含訂單摘要、分頁資訊及總筆數的 JSON 響應

#### Scenario: 非管理員請求拒絕
- **WHEN** 普通用戶請求 `/api/v1/admin/orders`
- **THEN** 系統返回 403 Forbidden 錯誤

### Requirement: 訂單詳情檢視
管理員 **SHALL** 能夠查看特定訂單的完整詳細資訊，包括商品清單、收件人資料及付款狀態。

#### Scenario: 成功獲取訂單詳情
- **WHEN** 管理員請求 `/api/v1/admin/orders/{order_id}` 且訂單存在
- **THEN** 系統返回包含完整訂單欄位與相關關聯資料的 JSON 響應

### Requirement: 更新訂單狀態
管理員 **MUST** 能夠手動更新訂單的執行狀態（Status）。

#### Scenario: 成功更新訂單狀態
- **WHEN** 管理員發送 PATCH 請求至 `/api/v1/admin/orders/{order_id}` 並提供新的 `status` (例如: "shipped")
- **THEN** 系統更新資料庫中該訂單的狀態，並記錄 `status_updated_at` 時間

#### Scenario: 無效的狀態跳轉拒絕
- **WHEN** 管理員嘗試將 "cancelled" 訂單更新為 "shipped"
- **THEN** 系統返回 400 Bad Request 並說明狀態轉換不合法

### Requirement: 管理員內部備註
訂單模型 **SHALL** 支援由管理員添加的內部備註欄位，此欄位對普通用戶不可見。

#### Scenario: 儲存管理員備註
- **WHEN** 管理員在更新訂單時提供 `admin_note` 內容
- **THEN** 系統將內容持久化至 `admin_note` 欄位，且該內容僅在管理端 API 返回
