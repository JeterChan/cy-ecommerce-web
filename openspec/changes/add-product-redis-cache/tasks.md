## 1. 快取服務核心

- [ ] 1.1 新增 `backend/src/infrastructure/product_cache_service.py`，實作 `ProductCacheService` 類別，包含：Redis 連線注入、JSON 序列化/反序列化、TTL 常數定義、所有操作的 try/except 降級處理
- [ ] 1.2 實作 `get_product_detail(product_id)` 方法：從 Redis 讀取 `product:detail:{product_id}` 並反序列化為 `ProductResponseDTO`
- [ ] 1.3 實作 `set_product_detail(product_id, dto)` 方法：將 `ProductResponseDTO` 序列化為 JSON 寫入 Redis，TTL 30 分鐘
- [ ] 1.4 實作 `get_product_list(params_hash)` 方法：從 Redis 讀取 `product:list:{params_hash}` 並反序列化
- [ ] 1.5 實作 `set_product_list(params_hash, data)` 方法：將列表結果序列化為 JSON 寫入 Redis，TTL 10 分鐘
- [ ] 1.6 實作 `build_list_cache_key(**params)` 靜態方法：將查詢參數排序後做 SHA256 hash 產生 cache key
- [ ] 1.7 實作 `invalidate_product_detail(product_id)` 方法：刪除 `product:detail:{product_id}` key
- [ ] 1.8 實作 `invalidate_all_product_lists()` 方法：使用 SCAN 指令刪除所有 `product:list:*` pattern 的 key

## 2. Use Case 層整合 — 讀取路徑

- [ ] 2.1 修改 `GetProductUseCase`：注入 `ProductCacheService`，在查詢前先讀取快取，cache miss 時查 DB 並回寫快取
- [ ] 2.2 修改 `ListProductsUseCase`：注入 `ProductCacheService`，根據查詢參數 hash 讀取列表快取，cache miss 時查 DB 並回寫快取

## 3. Use Case 層整合 — 寫入失效路徑

- [ ] 3.1 修改 `CreateProductUseCase`：在成功建立商品後呼叫 `invalidate_all_product_lists()`
- [ ] 3.2 修改 `UpdateProductUseCase`：在成功更新後呼叫 `invalidate_product_detail(product_id)` + `invalidate_all_product_lists()`
- [ ] 3.3 修改 `DeleteProductUseCase`：在成功刪除後呼叫 `invalidate_product_detail(product_id)` + `invalidate_all_product_lists()`
- [ ] 3.4 修改 `ToggleProductActiveUseCase`：在成功切換後呼叫 `invalidate_product_detail(product_id)` + `invalidate_all_product_lists()`
- [ ] 3.5 修改 `AdjustProductStockUseCase`：在成功調整庫存後呼叫 `invalidate_product_detail(product_id)`

## 4. Route Handler 注入

- [ ] 4.1 修改 `presentation/routes.py`：在商品列表與詳情的 route handler 中注入 Redis 依賴，建立 `ProductCacheService` 並傳入 use case
- [ ] 4.2 修改 `presentation/admin_routes.py`：在管理員的新增、更新、刪除、上下架 route handler 中注入 Redis 依賴，建立 `ProductCacheService` 並傳入 use case

## 5. 測試

- [ ] 5.1 為 `ProductCacheService` 撰寫單元測試：涵蓋 cache hit/miss、invalidation、SCAN 刪除、Redis 異常降級等場景
- [ ] 5.2 為修改後的 use case 撰寫單元測試：驗證讀取路徑的快取整合與寫入路徑的快取失效呼叫
- [ ] 5.3 執行既有測試確保無 regression
