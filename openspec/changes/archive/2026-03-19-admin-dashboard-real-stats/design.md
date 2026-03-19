## Context

Admin dashboard (`AdminDashboard.vue`) 目前顯示 4 個 hardcoded 統計數字。後端已有 product 與 order 的 admin routes，但沒有 dashboard 統計專用端點。專案採用 Clean Architecture，每個模組有 domain/application/infrastructure/presentation 四層。

目前相關程式碼：
- `backend/src/modules/product/infrastructure/repository.py` — 有 `list_admin()` 但無聚合統計方法
- `backend/src/modules/order/infrastructure/repositories/postgres_order_repository.py` — 有 `count_all()` 但無今日篩選或 SUM
- `frontend/src/views/admin/AdminDashboard.vue` — 4 個 hardcoded stat cards
- 低庫存定義：`0 < stock_quantity < 5`（來自 `ProductResponseDTO.is_low_stock`）

## Goals / Non-Goals

**Goals:**
- 新增 `GET /api/v1/admin/dashboard/stats` 端點，回傳四項統計
- 後端遵循現有 Clean Architecture 模式（use case + DTO + repository method）
- 前端替換 hardcoded 數據，加入 loading/error 狀態

**Non-Goals:**
- 不加快取（Redis）—資料量小，查詢快速
- 不做歷史趨勢或時間範圍篩選
- 不新增獨立的 admin 模組，統計邏輯分散於 product/order 現有模組

## Decisions

### 1. 端點位置：使用 product admin routes 或獨立路由？

**決定**：在 `backend/src/modules/product/presentation/admin_routes.py` 加入新路由，因為 dashboard stats 主要是彙總查詢，且避免新建模組。

**Alternative considered**：新建 `backend/src/modules/dashboard/` 模組 — 過度工程，當前 4 個統計不需要獨立模組。

### 2. Repository 方法：擴充現有 repo vs. 新增 stats use case 直接下 raw SQL？

**決定**：在 `ProductRepository` 新增 `count_total_active()` 與 `count_low_stock()`；在 `PostgresOrderRepository` 新增 `get_today_stats()`（回傳 count + sum）。由新 `GetDashboardStatsUseCase` 組合兩個 repo 呼叫。

**Rationale**：維持 repository pattern 一致性，避免 use case 直接存取 DB session。

### 3. 今日銷售額定義

**決定**：今日以台灣時區（UTC+8）的 `CURRENT_DATE AT TIME ZONE 'Asia/Taipei'` 計算，並排除 `CANCELLED` 與 `REFUNDED` 狀態的訂單。

### 4. DTO 結構

```python
class DashboardStatsDTO(BaseModel):
    total_products: int
    low_stock_count: int
    today_orders: int
    today_sales: Decimal
```

## Risks / Trade-offs

- **低庫存閾值** → 目前 hardcode 為 5，未來若需要可設定化；此次不處理
- **前端無快取** → 每次進入 dashboard 都發 request；統計查詢快速，可接受

## Migration Plan

1. 後端：新增 repository 方法 → use case → DTO → route handler（不影響現有 API）
2. 前端：新增 service → 修改 `AdminDashboard.vue`（移除 mock data，加入 API 呼叫）
3. 無 DB schema 變更，無需 migration
4. Rollback：只需 revert frontend 改動即可恢復 mock data 顯示

## Open Questions

- 無
