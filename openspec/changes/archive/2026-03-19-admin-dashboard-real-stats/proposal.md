## Why

Admin dashboard 目前顯示的商品總數、低庫存警示、今日訂單、銷售額均為 hardcoded mock 數據，無法反映真實業務狀態。需替換為從資料庫動態取得的真實數據，讓管理員能做出正確決策。

## What Changes

- 新增後端 `/api/v1/admin/dashboard/stats` API endpoint，回傳四項統計數據
- 在 product 及 order repository 新增 stats 查詢方法（商品總數、低庫存商品數、今日訂單數、今日銷售額）
- 新增前端 `adminDashboardService.ts` 呼叫 stats API
- 更新 `AdminDashboard.vue`：移除 hardcoded 數據，改為 API 取得的真實數據，含 loading 狀態

## Capabilities

### New Capabilities

- `admin-dashboard-stats`: 提供 admin dashboard 四項統計數據的 API 端點及前端整合（商品總數、低庫存警示數、今日訂單數、今日銷售額）

### Modified Capabilities

<!-- 無現有 spec 需要修改 -->

## Impact

- **Backend**: 新增 `GET /api/v1/admin/dashboard/stats` route；擴充 `ProductRepository` 與 `OrderRepository` 新增統計查詢；新增對應 use case 與 DTO
- **Frontend**: 新增 `adminDashboardService.ts`；修改 `AdminDashboard.vue` 移除 mock data
- **資料庫**: 僅 SELECT 查詢，無 schema 變更
