# Quickstart: Member Cart Async Sync (Celery)

## 1. 啟動環境
- 確保 **Redis** 已啟動。
- 確保 **Celery Worker** 已啟動：
  ```bash
  celery -A core.celery worker --loglevel=info -Q cart_sync_queue
  ```

## 2. 測試步驟
1. **觸發更新**: 使用會員權限呼叫 `POST /api/v1/cart/items`。
2. **驗證 Redis**:
   ```bash
   redis-cli HGETALL cart:{user_id}
   ```
   應立即看到更新。
3. **觀察 Celery**: 查看 Worker 終端機是否有 `sync_member_cart_task` 的執行紀錄。
4. **驗證 PostgreSQL**:
   ```sql
   SELECT * FROM cart_items WHERE user_id = '...';
   ```
   應在 2 秒內看到與 Redis 同步後的結果。

## 3. 故障測試
- 停止 Celery Worker，呼叫 API 更新購物車。
- 確認 Redis 正常更新，但 PostgreSQL 保持舊狀態。
- 啟動 Celery Worker，確認任務被自動消費，PostgreSQL 數據恢復一致。
