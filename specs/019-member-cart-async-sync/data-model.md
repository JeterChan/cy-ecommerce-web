# Data Model: Member Cart Async Sync

## Entities

### 1. Redis Cart State (Cache)
- **Key**: `cart:{user_id}` (Hash)
- **Fields**: `{product_id}`
- **Value**: JSON `{ "quantity": int, "updated_at": timestamp }`

### 2. Celery Task Message (Queue)
- **Queue Name**: `cart_sync_queue`
- **Payload**: `{ "user_id": UUID, "triggered_at": ISO8601 }`

### 3. PostgreSQL Cart Items (Persistence)
- **Table**: `cart_items` (現有)
- **Key Fields**:
  - `user_id`: UUID (FK)
  - `product_id`: UUID (FK)
  - `quantity`: Integer
  - `updated_at`: DateTime

## State Transitions & Validation

### API Update Flow
1. API 接收 `POST/PATCH/DELETE` 請求。
2. 執行業務校驗（如庫存檢查）。
3. **原子性寫入 Redis**: `HSET cart:{user_id} {product_id} {new_data}`。
4. **發送同步任務**: `sync_member_cart_task.apply_async(args=[user_id], queue='cart_sync_queue')`。

### Background Sync Flow (Celery Worker)
1. 接收 `user_id`。
2. 嘗試獲取 Redis 鎖 `lock:cart_sync:{user_id}` (防止併發任務衝突)。
3. 從 Redis 讀取該會員的完整購物車清單。
4. 開啟資料庫事務：
   - 清除該會員在 DB 的舊數據 (或執行 UPSERT 邏輯)。
   - 批量寫入最新狀態。
5. 釋放 Redis 鎖。
6. 完成任務。
