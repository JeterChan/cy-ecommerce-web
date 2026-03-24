## Why

後端程式碼的單元測試覆蓋率嚴重不足。目前僅 auth 模組有部分 use case 單元測試，而 product、cart、order 模組的 domain 層與 application 層幾乎完全沒有單元測試。跨模組的 `StockRedisService` 也缺乏測試。補齊單元測試可在不依賴外部服務的情況下，快速驗證核心業務邏輯的正確性，降低回歸風險。

## What Changes

- 為 **product** 模組新增 domain entity 單元測試（`Product.validate()`、`Product.update_stock()`、`Category.validate()`）與 use case 單元測試（`CreateProductUseCase`、`AdjustProductStockUseCase`）
- 為 **cart** 模組新增 use case 單元測試（`AddToCartUseCase`、`UpdateCartItemQuantityUseCase`、`MergeCartUseCase`）與 service 單元測試（`CartMergeService`）
- 為 **order** 模組新增 domain entity 單元測試（`Order.validate()`、`OrderItem.validate()`）與 use case 單元測試（`CheckoutUseCase`、`UpdateOrderStatusUseCase`）
- 為跨模組的 **StockRedisService** 新增完整單元測試（`try_deduct`、`rollback`、`sync_stock`、lazy-init 路徑）
- 補強 **auth** 模組現有測試缺口（`DeleteAccountUseCase`、`UpdateProfileUseCase`）

## Capabilities

### New Capabilities

- `backend-unit-tests`: 後端各模組的 domain 層與 application 層單元測試，使用 mock 隔離外部依賴，涵蓋 auth、product、cart、order 四個模組及 StockRedisService

### Modified Capabilities

（無需修改現有 spec 的 requirement）

## Impact

- 新增測試檔案於 `backend/tests/unit/modules/{product,cart,order}/` 及 `backend/tests/unit/infrastructure/`
- 補強 `backend/tests/unit/modules/auth/` 的現有測試
- 不影響任何正式程式碼、API 或資料庫 schema
- 可能需新增測試用的 `conftest.py` 提供共用 fixture
