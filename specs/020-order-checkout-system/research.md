# Research: Order Checkout Transaction and Concurrency Protection

## 1. 併發庫存扣除策略 (Concurrency Stock Deduction)

### 決策：使用 PostgreSQL 行級鎖 (Row-level Locking)
- **方案**: 在資料庫事務中，使用 `SELECT ... FOR UPDATE` 鎖定待購買的產品行。
- **理由**: 
    - 確保在扣除庫存期間，其他事務無法修改同一產品的庫存數量。
    - 相比於樂觀鎖 (Optimistic Locking)，在商品熱賣（高競爭）時，`FOR UPDATE` 能更直接地管理排隊請求，避免頻繁的重試失敗。
    - 現有的 `atomic_adjust_stock` 需要改造成支援在現有事務中執行，並使用強大的鎖定機制。

## 2. 事務範圍與原子性 (Transaction Scope)

### 決策：一站式資料庫事務 (Single DB Transaction)
- **步驟**:
    1. 開啟異步資料庫事務。
    2. 執行 `SELECT ... FOR UPDATE` 批量獲取產品資訊並鎖定行。
    3. 業務驗證：檢查產品是否存在、是否上架、庫存是否充足、價格是否變動。
    4. 執行扣除：`UPDATE products SET stock_quantity = stock_quantity - :qty WHERE id = :id`。
    5. 寫入 `orders` 表。
    6. 批量寫入 `order_items` 表。
    7. 提交 (Commit) 事務。
- **例外處理**: 任何步驟失敗皆執行 `Rollback`，確保不會出現庫存已扣但訂單未建立的情況。

## 3. Redis 與 DB 的一致性協調

### 決策：Post-Commit Redis Cleanup
- **方案**: Redis 購物車的清除操作 (Delete) 必須放在資料庫事務 `commit()` 成功之後。
- **理由**: 
    - 若放在事務內，Redis 無法隨資料庫一同回滾。
    - 若事務成功但 Redis 刪除失敗，使用者頂多看到購物車還有東西（可透過前端或背景任務補償），但不會造成金流或庫存損失。這符合「最終一致性」的務實做法。

## 4. 併發防超賣的實作細節

### SQL 實作建議
```sql
-- 鎖定多行產品，按 ID 排序以防止死鎖 (Deadlock)
SELECT id, stock_quantity, price, is_active 
FROM products 
WHERE id IN (:ids) 
ORDER BY id 
FOR UPDATE;
```

## 5. 考慮替代方案 (Alternatives Considered)

- **Redis Lua Script 扣庫存**: 
    - *優點*: 極快。
    - *缺點*: 庫存真理來源在 PostgreSQL，若 Redis 崩潰或數據不同步會造成麻煩。為了 MVP 階段的資料一致性，選擇 PostgreSQL 作為真理來源。
- **Optimistic Locking (`version` column)**:
    - *優點*: 無鎖定，讀取快。
    - *缺點*: 高併發下衝突率高，會導致大量結帳失敗。結帳流程應優先保證成功率而非極致的讀取效能。
