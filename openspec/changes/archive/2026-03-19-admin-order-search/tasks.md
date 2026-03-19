## 1. 後端：Repository 介面與實作

- [x] 1.1 更新 `IOrderRepository.list_all` 介面，新增 `search_order_number`、`search_recipient_name`、`search_phone`、`date_from`、`date_to` 五個可選參數
- [x] 1.2 更新 `IOrderRepository.count_all` 介面，同步新增相同五個可選參數
- [x] 1.3 實作 `PostgresOrderRepository.list_all`：依各非空參數加入 ILIKE / 日期範圍 WHERE 條件（AND 組合）
- [x] 1.4 實作 `PostgresOrderRepository.count_all`：套用相同篩選條件

## 2. 後端：Use Case 與 API 路由

- [x] 2.1 更新 `AdminListOrdersUseCase.execute`，接受並傳遞五個新參數至 repository
- [x] 2.2 更新 `admin_routes.py` 的 `admin_list_orders`，新增五個 `Query` 參數（`Optional[str]` × 3，`Optional[date]` × 2）並傳入 use case

## 3. 前端：Service 層

- [x] 3.1 更新 `AdminOrderSearchParams` 介面，新增 `search_order_number`、`search_recipient_name`、`search_phone`、`date_from`、`date_to` 欄位
- [x] 3.2 更新 `adminOrderService.getOrders()`，將新欄位（非空時）加入 query string

## 4. 前端：UI 更新

- [x] 4.1 移除既有單一 `searchId` ref，新增五個獨立 ref：`searchOrderNumber`、`searchRecipientName`、`searchPhone`、`dateFrom`、`dateTo`
- [x] 4.2 更新 `loadOrders()` 呼叫，傳入所有新篩選參數
- [x] 4.3 新增 `resetFilters()` 函式，清空所有搜尋欄位並觸發查詢
- [x] 4.4 改寫篩選器 Card UI：第一排（訂單編號、收件人姓名、電話）、第二排（開始日期、結束日期、狀態下拉），底部操作列（重置篩選、搜尋、重新整理）
- [x] 4.5 訂單列表表格新增「收件人」欄位（`order_number` 欄之後）
