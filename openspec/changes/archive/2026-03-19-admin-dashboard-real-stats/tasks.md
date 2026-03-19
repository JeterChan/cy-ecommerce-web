## 1. Backend — Repository 統計方法

- [x] 1.1 在 `ProductRepository` 新增 `count_total_active()` 方法，查詢 `is_active = true` 的商品總數
- [x] 1.2 在 `ProductRepository` 新增 `count_low_stock()` 方法，查詢 `is_active = true` 且 `0 < stock_quantity < 5` 的商品數
- [x] 1.3 在 `PostgresOrderRepository` 新增 `get_today_stats()` 方法，查詢台灣時區（Asia/Taipei）當日有效訂單數及銷售額（排除 CANCELLED、REFUNDED）

## 2. Backend — Application 層（Use Case + DTO）

- [x] 2.1 新增 `DashboardStatsDTO` (Pydantic BaseModel)，欄位：`total_products: int`、`low_stock_count: int`、`today_orders: int`、`today_sales: Decimal`
- [x] 2.2 新增 `GetDashboardStatsUseCase`，注入 `ProductRepository` 與 `OrderRepository`，組合呼叫兩個 repo 方法並回傳 `DashboardStatsDTO`

## 3. Backend — Presentation 層（API Route）

- [x] 3.1 在 `backend/src/modules/product/presentation/admin_routes.py` 新增 `GET /api/v1/admin/dashboard/stats` 路由，呼叫 `GetDashboardStatsUseCase` 並回傳 `DashboardStatsDTO`，需要 admin JWT 認證

## 4. Frontend — Service 層

- [x] 4.1 新增 `frontend/src/services/adminDashboardService.ts`，提供 `getDashboardStats()` 函式呼叫 `GET /api/v1/admin/dashboard/stats`，定義對應 TypeScript interface

## 5. Frontend — Dashboard 元件

- [x] 5.1 更新 `AdminDashboard.vue`：移除 hardcoded mock 數值，新增 `ref` 儲存 stats 資料及 loading 狀態
- [x] 5.2 在 `onMounted` 呼叫 `getDashboardStats()`，loading 期間顯示佔位符（"..."）
- [x] 5.3 將 `today_sales` 以 `NT$ X,XXX` 格式格式化顯示
