## Why

各後端模組（Cart、Order、Auth）目前在 Presentation 層直接 import 其他模組的具體實作類別（如 `SqlAlchemyProductRepository`、`ProductModel`、`CartMergeService`），導致模組間產生不必要的耦合。當某個模組的 infrastructure 實作變更時，會波及其他模組的路由層程式碼。應統一採用 Adapter 模式（參考現有 `OrderCartAdapter` 的成功實踐），讓每個模組只依賴自己 Domain 層定義的介面。

## What Changes

- **Cart 模組**：新增 `IProductInfoPort` 介面（Domain 層）與 `ProductInfoAdapter`（Infrastructure 層），取代 Presentation 層直接 import `SqlAlchemyProductRepository` 的做法
- **Order 模組**：新增 `IProductPort` 介面（Domain 層）與 `OrderProductAdapter`（Infrastructure 層），取代 `checkout.py` 直接 import `ProductModel` 以及路由層直接實例化 `SqlAlchemyProductRepository` 的做法；同時改善現有 `ICartAdapter` 確保 checkout use case 不再直接操作 Cart 模組的具體類別
- **Auth 模組**：新增 `ICartMergePort` 介面（Domain 層）與 `CartMergeAdapter`（Infrastructure 層），取代登入路由直接 import `CartMergeService` 和 `get_guest_token_from_cookie` 的做法

## Capabilities

### New Capabilities
- `module-adapter-pattern`: 定義各模組跨模組依賴的 Port/Adapter 介面與實作，統一解耦策略

### Modified Capabilities
- `order-checkout-system`: 結帳流程的跨模組依賴方式改變，checkout use case 不再直接 import `ProductModel`，改為透過 `IProductPort` 介面操作

## Impact

- **受影響的程式碼**：
  - `backend/src/modules/cart/presentation/routes.py` — 移除對 `SqlAlchemyProductRepository` 的直接 import
  - `backend/src/modules/cart/application/use_cases/cart_commands.py` — 改為依賴 Cart 自己的 Port 介面
  - `backend/src/modules/order/application/use_cases/checkout.py` — 移除對 `ProductModel` 的直接 import，改用 Port 介面
  - `backend/src/modules/order/application/use_cases/update_order_status.py` — 改為依賴 Order 自己的 Port 介面
  - `backend/src/modules/order/presentation/routes.py` — 改用 Adapter 實例化
  - `backend/src/modules/auth/presentation/routes.py` — 移除對 Cart 模組具體類別的直接 import
- **API 行為**：無變更，所有端點行為維持不變
- **測試**：現有單元測試中 mock 的介面名稱可能需要更新
