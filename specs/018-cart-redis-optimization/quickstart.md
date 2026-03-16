# Quickstart: Cart Redis Optimization (DDD Alignment)

## 1. 驗證現有 Redis 儲存結構
- **步驟**: 在未修改代碼前，使用 `POST /api/v1/cart/items` 加入商品。
- **檢查**: 使用 `redis-cli HGETALL cart:{token}`。
- **預期**: 應僅包含 `product_id` 和 `quantity`（目前 JSON 內含此二者及時間戳，符合 FR-001 最低要求）。

## 2. 驗證庫存鎖定校驗 (本功能核心)
- **步驟**:
  1. 準備商品，庫存設為 5。
  2. 使用 `POST /api/v1/cart/items` 嘗試加入 6 個。
- **預期**: 應返回 `400 Bad Request` 且包含「庫存不足」訊息 (FR-005)。
- **技術檢查**: 查看資料庫日誌或測試日誌，確認是否有 `SELECT ... FOR SHARE` 的 SQL 出現。

## 3. 驗證動態價格更新
- **步驟**:
  1. 加入商品 A (價格 100) 到購物車。
  2. 呼叫 `GET /api/v1/cart`。
  3. 修改資料庫中商品 A 的價格為 200。
  4. 再次呼叫 `GET /api/v1/cart`。
- **預期**: 第二次呼叫應顯示單價為 200，且小計與總額正確更新 (FR-004, SC-002)。
