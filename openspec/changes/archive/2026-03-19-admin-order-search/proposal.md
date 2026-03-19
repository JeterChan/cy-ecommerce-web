## Why

目前後台訂單管理只支援狀態篩選與分頁，管理員無法直接用訂單編號、收件人姓名或電話快速定位訂單，也無法依日期範圍縮小查詢範圍，導致訂單量增長後查找效率低落。

## What Changes

- 後端 `GET /api/v1/admin/orders` 新增五個查詢參數：`search_order_number`、`search_recipient_name`、`search_phone`、`date_from`、`date_to`
- Repository 介面與實作新增對應篩選邏輯（AND 組合，ILIKE 模糊匹配文字欄位，範圍查詢日期）
- `AdminListOrdersUseCase` 傳遞新參數至 repository
- 前端 `AdminOrderSearchParams` 介面擴充五個新欄位
- 前端 `adminOrderService.getOrders()` 將新欄位加入 query string
- 前端篩選 UI 由單一搜尋框改為多欄位表單（訂單編號、收件人姓名、電話、開始/結束日期、狀態）
- 訂單列表表格新增「收件人」欄位
- 新增「重置篩選」按鈕

## Capabilities

### New Capabilities

- `admin-order-search`: 管理員訂單多欄位搜尋，涵蓋後端篩選邏輯與前端搜尋表單 UI

### Modified Capabilities

（無）

## Impact

- **後端**：`admin_routes.py`、`admin_list_orders.py`、`postgres_order_repository.py`、`repository.py`（介面）
- **前端**：`adminOrderService.ts`、`OrderManagementView.vue`
- **無資料庫 migration**：僅使用現有欄位查詢，`order_number`、`created_at` 已有 index
