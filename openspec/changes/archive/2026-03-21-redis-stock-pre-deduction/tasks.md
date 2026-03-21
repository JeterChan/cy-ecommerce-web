## 1. StockRedisService 建立

- [x] 1.1 建立 `backend/src/infrastructure/stock_redis_service.py`，實作 `StockRedisService` class，包含 `init_stock(product_id, quantity)`、`try_deduct(product_id, quantity)` → `(success, remaining)`、`rollback(product_id, quantity)`、`get_stock(product_id)` 四個方法
- [x] 1.2 `try_deduct` 實作：執行 `DECRBY`，若結果 < 0 則自動 `INCRBY` 回滾並回傳 `(False, 0)`；>= 0 回傳 `(True, remaining)`
- [x] 1.3 `try_deduct` 加入 lazy init：若 key 不存在（`DECRBY` 對不存在 key 回傳負數），從 DB 讀取庫存初始化 Redis 後重試一次

## 2. CheckoutUseCase 整合 Redis 預扣

- [x] 2.1 修改 `checkout.py` 的 `execute()` 方法，在 `_perform_checkout` 之前新增 Redis 預扣邏輯：遍歷購物車商品依序呼叫 `StockRedisService.try_deduct`
- [x] 2.2 實作多商品回滾：若任一商品預扣失敗，回滾所有已成功預扣的商品，拋出 `InsufficientStockException`
- [x] 2.3 實作 DB 事務失敗回滾：用 try/except 包裹 DB 事務，失敗時呼叫 `StockRedisService.rollback` 回滾所有商品

## 3. 商品管理同步 Redis 庫存

- [x] 3.1 修改 `CreateProductUseCase`：商品建立成功後呼叫 `StockRedisService.init_stock` 初始化 Redis 庫存
- [x] 3.2 修改 `AdjustProductStockUseCase`：庫存調整成功後呼叫 `StockRedisService.sync_stock` 同步 Redis delta

## 4. 依賴注入與路由整合

- [x] 4.1 修改 `order/presentation/routes.py` 的 `checkout` endpoint：建立 `StockRedisService` 實例並傳入 `CheckoutUseCase`
- [x] 4.2 修改 `product/presentation/routes.py` 和 `admin_routes.py`：在建立商品和調整庫存的 endpoint 中建立 `StockRedisService` 實例並傳入 use case

## 5. 壓力測試驗證

- [x] 5.1 使用現有 k6 壓力測試腳本執行 100/500/1000/2000 VU 測試，驗證庫存完整性仍為 PASS 且回應時間顯著改善
