## Context

後台訂單管理現有架構：`GET /api/v1/admin/orders` 僅接受 `status`、`page`、`limit` 三個查詢參數。前端 `OrderManagementView.vue` 已有 `searchId` ref 和 Search icon，但從未傳送至後端——是個未完成的骨架。

Repository 的 `list_all` / `count_all` 僅對 `status` 做 WHERE 條件，使用 SQLAlchemy async 查詢。`order_number` 和 `created_at` 欄位已有 index，適合搜尋。

## Goals / Non-Goals

**Goals:**
- 後端 API 支援五個新搜尋參數（訂單編號、收件人姓名、電話、日期起訖）
- 所有條件以 AND 邏輯組合，未填欄位不加入查詢
- 前端更新為多欄位搜尋表單，表格補充收件人欄位

**Non-Goals:**
- 全文搜尋（Full-text search）
- 跨模組搜尋（例如依商品名稱搜尋訂單）
- 搜尋結果排序切換
- 資料庫 migration（只用既有欄位）

## Decisions

### 文字欄位使用 ILIKE 模糊搜尋

`order_number`、`recipient_name`、`recipient_phone` 皆用 `ILIKE '%value%'`。

替代方案：prefix 搜尋（`ILIKE 'value%'`）可利用 index 但體驗較差；精確搜尋則對管理員輸入習慣不友善。管理員通常只記得部分資訊，模糊搜尋最實用。`order_number` 雖有 index，ILIKE 含前置 `%` 會 sequential scan，訂單量在 OLTP 規模下可接受。

### `date_to` 包含當日至 23:59:59

查詢時轉換為 `date_to + timedelta(days=1)`（等同 `< date_to + 1 day`），或直接 `<= date_to 23:59:59.999999`。選用前者實作較簡潔：

```python
from datetime import datetime, timedelta
end = datetime.combine(date_to, datetime.max.time())
stmt = stmt.where(OrderModel.created_at <= end)
```

### 前端表單「搜尋」按鈕觸發，非即時搜尋

多欄位表單若每個輸入都即時觸發 API，會產生大量請求。統一由「搜尋」按鈕（或 Enter 鍵）觸發，「重置篩選」一鍵清空所有條件並重新查詢。

### 日期輸入使用原生 `<input type="date">`

專案沒有 DatePicker 元件，使用原生 `<input type="date">` 並套用與 shadcn Input 相同的 class，保持 UI 一致性，無需新增依賴。

### `IOrderRepository` 介面同步更新

`list_all` 和 `count_all` 新增五個可選參數，保持介面與實作同步，讓未來的 mock 或測試 repository 也必須實作。

## Risks / Trade-offs

- **ILIKE 效能**：含前置 `%` 的 LIKE 無法使用 btree index，訂單量達數十萬筆時查詢可能變慢 → 短期可接受，未來可加 pg_trgm index 或限制搜尋字元數
- **前端 `date_from`/`date_to` 格式**：原生 `<input type="date">` 回傳 `YYYY-MM-DD` 字串，後端需正確解析為 `date` 型別 → FastAPI Query 參數宣告為 `Optional[date]` 即可自動轉換

## Migration Plan

無資料庫 migration 需求。後端新參數皆為 Optional，既有 API 呼叫不受影響（向後相容）。前端改動僅限後台訂單頁面。
