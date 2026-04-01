## 1. Cart 模組：Port/Adapter 建立

- [x] 1.1 在 `cart/domain/ports.py` 定義 `IProductInfoPort` 介面與 `ProductSnapshot` 值物件
- [x] 1.2 在 `cart/infrastructure/adapters/product_info_adapter.py` 實作 `ProductInfoAdapter`，橋接 `SqlAlchemyProductRepository`
- [x] 1.3 重構 `cart/application/use_cases/cart_commands.py`，將 `IProductRepository` 替換為 `IProductInfoPort`
- [x] 1.4 重構 `cart/presentation/routes.py`，移除 `SqlAlchemyProductRepository` 的直接 import，改用 `ProductInfoAdapter`

## 2. Order 模組：Product Port/Adapter 建立

- [x] 2.1 在 `order/domain/ports.py` 定義 `IProductPort` 介面與 `CheckoutProduct` 值物件
- [x] 2.2 在 `order/infrastructure/adapters/order_product_adapter.py` 實作 `OrderProductAdapter`，封裝悲觀鎖查詢與庫存扣減/回補邏輯
- [x] 2.3 重構 `order/application/use_cases/checkout.py`，移除 `ProductModel` 直接 import，改用 `IProductPort`
- [x] 2.4 重構 `order/application/use_cases/update_order_status.py`，將 `IProductRepository` 替換為 `IProductPort`
- [x] 2.5 重構 `order/application/use_cases/admin_update_order.py`（若存在類似耦合），改用 `IProductPort`

## 3. Order 模組：Cart Adapter 擴展

- [x] 3.1 擴展 `OrderCartAdapter` 支援接受 `ICartRepository`（含 `HybridCartRepository`），而非僅限 `RedisCartRepository`
- [x] 3.2 重構 `order/presentation/routes.py`，移除 `HybridCartRepository` 的直接 import，改用擴展後的 `OrderCartAdapter`

## 4. Auth 模組：Cart Merge Port/Adapter 建立

- [x] 4.1 在 `auth/domain/ports.py` 定義 `ICartMergePort` 介面
- [x] 4.2 在 `auth/infrastructure/adapters/cart_merge_adapter.py` 實作 `CartMergeAdapter`，橋接 `CartMergeService` 和 `get_guest_token_from_cookie`
- [x] 4.3 重構 `auth/presentation/routes.py`，移除 Cart 模組的直接 import，改用 `CartMergeAdapter`

## 5. Order Presentation 層清理

- [x] 5.1 重構 `order/presentation/routes.py`，移除 `SqlAlchemyProductRepository` 的直接 import，改用 `OrderProductAdapter`
- [x] 5.2 重構 `order/presentation/admin_routes.py`，移除 `SqlAlchemyProductRepository` 的直接 import，改用 `OrderProductAdapter`

## 6. 驗證與測試

- [x] 6.1 執行 import 隔離檢查：確認 Cart/Order/Auth 的 presentation/ 和 application/ 不含跨模組 infrastructure import
- [x] 6.2 執行現有單元測試，修復因介面變更導致的測試失敗
- [x] 6.3 手動測試結帳流程（含庫存扣減、訂單取消還庫存），確認行為不變
