## ADDED Requirements

### Requirement: Dashboard stats API endpoint
系統 SHALL 提供 `GET /api/v1/admin/dashboard/stats` 端點，回傳 admin dashboard 所需的四項統計數據，僅限具有 admin 權限的使用者存取。

回應格式：
```json
{
  "total_products": 128,
  "low_stock_count": 5,
  "today_orders": 12,
  "today_sales": "42500.00"
}
```

#### Scenario: Admin 成功取得 dashboard 統計
- **WHEN** admin 使用有效 JWT token 呼叫 `GET /api/v1/admin/dashboard/stats`
- **THEN** 系統回傳 HTTP 200，包含 `total_products`、`low_stock_count`、`today_orders`、`today_sales` 四個欄位

#### Scenario: 未認證使用者存取被拒
- **WHEN** 未帶 token 或非 admin 使用者呼叫此端點
- **THEN** 系統回傳 HTTP 401 或 403

### Requirement: 商品總數統計
系統 SHALL 統計資料庫中 `is_active = true` 的商品總數作為 `total_products`。

#### Scenario: 計算啟用商品數
- **WHEN** 資料庫中有 N 筆 `is_active = true` 的商品
- **THEN** `total_products` 回傳 N

#### Scenario: 停用商品不計入
- **WHEN** 資料庫中有停用商品（`is_active = false`）
- **THEN** 停用商品不計入 `total_products`

### Requirement: 低庫存警示統計
系統 SHALL 統計 `is_active = true` 且 `0 < stock_quantity < 5` 的商品數量作為 `low_stock_count`。

#### Scenario: 計算低庫存商品數
- **WHEN** 資料庫中有商品庫存量介於 1 到 4 之間且為啟用狀態
- **THEN** `low_stock_count` 回傳符合條件的商品數

#### Scenario: 庫存為 0 的商品不計入低庫存
- **WHEN** 商品 `stock_quantity = 0`
- **THEN** 該商品不計入 `low_stock_count`（已無庫存，非低庫存）

### Requirement: 今日訂單數統計
系統 SHALL 統計台灣時區（UTC+8，Asia/Taipei）當日建立的訂單數量作為 `today_orders`，不含 `CANCELLED` 和 `REFUNDED` 狀態的訂單。

#### Scenario: 計算今日有效訂單
- **WHEN** 台灣時區當日有 N 筆非 CANCELLED/REFUNDED 訂單
- **THEN** `today_orders` 回傳 N

#### Scenario: 已取消或退款訂單不計入
- **WHEN** 今日有 CANCELLED 或 REFUNDED 狀態的訂單
- **THEN** 這些訂單不計入 `today_orders`

### Requirement: 今日銷售額統計
系統 SHALL 加總台灣時區（UTC+8，Asia/Taipei）當日建立的有效訂單（排除 `CANCELLED`、`REFUNDED` 狀態）的 `total_amount` 作為 `today_sales`。當日無訂單時回傳 `"0.00"`。

#### Scenario: 計算今日銷售額
- **WHEN** 台灣時區當日有有效訂單且 total_amount 之和為 S
- **THEN** `today_sales` 回傳 S（Decimal 字串，保留兩位小數）

#### Scenario: 今日無訂單時銷售額為零
- **WHEN** 台灣時區當日無任何有效訂單
- **THEN** `today_sales` 回傳 `"0.00"`

### Requirement: 前端 Dashboard 顯示真實數據
`AdminDashboard.vue` SHALL 在元件掛載時呼叫 dashboard stats API，並以真實數據渲染四個統計卡片，取代 hardcoded mock 數值。

#### Scenario: Dashboard 載入時顯示 loading 狀態
- **WHEN** 元件掛載，API 請求尚未完成
- **THEN** 統計卡片顯示 loading 指示（如 skeleton 或 "..." 佔位符）

#### Scenario: API 成功後顯示真實數據
- **WHEN** API 回傳成功
- **THEN** 四個統計卡片分別顯示 `total_products`、`low_stock_count`、`today_orders`、`today_sales`

#### Scenario: 銷售額格式化顯示
- **WHEN** API 回傳 `today_sales`
- **THEN** 前端以 `NT$ X,XXX` 格式顯示銷售額
