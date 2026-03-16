# Cart Redis Optimization & Stock Validation (DDD Alignment)

## 實作總結

本功能已成功實作於專案的 DDD 架構中，整合了 `Cart` 與 `Product` 模組。

### 核心變更

1. **資料庫鎖定實作**:
   - 在 `SqlAlchemyProductRepository` 中新增 `get_by_id_with_lock`。
   - 使用 PostgreSQL `FOR SHARE` 鎖定，確保在庫存校驗期間商品庫存不會被修改。

2. **跨模組業務邏輯**:
   - 將 `IProductRepository` 注入 `AddToCartUseCase` 與 `UpdateCartItemQuantityUseCase`。
   - 在更新購物車（Redis）前，先從資料庫獲取最新庫存並進行校驗。

3. **輕量化儲存與動態定價**:
   - 確認現有 `RedisCartRepository` 僅儲存 `product_id` 與 `quantity`。
   - 複用現有的 `enrich_cart_items_with_product_info` 機制，在讀取時動態獲取最新價格。

4. **異常處理**:
   - 定義了 `InsufficientStockException`，並透過全局 `domain_exception_handler` 返回統一的 400 錯誤。

### 驗證結果

- **US1 (加入與校驗)**: 已通過集成測試，證實超過庫存時會拋出異常。
- **US2 (動態定價)**: 測試證實資料庫價格變動後，購物車總額會即時更新。
- **效能**: Redis 與資料庫鎖定操作均在預期時間範圍內。

## 執行指令
```bash
pytest backend/tests/integration/test_cart_redis_optimization.py
```
