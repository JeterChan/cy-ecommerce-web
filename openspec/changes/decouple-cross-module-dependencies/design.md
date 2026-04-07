## Context

目前專案的 Clean Architecture 在 Domain/Application 層大致遵循介面隔離，但 Presentation 層（路由）普遍直接 import 其他模組的具體 Infrastructure 類別。唯一做到完整解耦的是 Order → Cart 的 `OrderCartAdapter`，它在 Order 的 Domain 層定義 `ICartAdapter` 介面，再由 Infrastructure 層的 `OrderCartAdapter` 橋接 Cart 模組。

現況耦合點：
1. **Cart routes** 直接 import `SqlAlchemyProductRepository` 來做商品資訊富化與庫存校驗
2. **Order routes** 直接 import `SqlAlchemyProductRepository`；`checkout.py` 直接 import `ProductModel` 做 ORM 操作
3. **Auth routes** 直接 import `CartMergeService` 和 `get_guest_token_from_cookie`
4. **Order routes** 直接 import `HybridCartRepository`（checkout 流程）

## Goals / Non-Goals

**Goals:**
- 每個模組的 Domain 層定義自己需要的 Port 介面（跨模組依賴）
- 每個模組的 Infrastructure 層提供 Adapter 實作，橋接外部模組
- Presentation 層只實例化本模組的 Adapter，不再 import 其他模組的具體類別
- 保持所有 API 端點行為完全不變

**Non-Goals:**
- 不引入 DI 容器框架（如 dependency-injector），維持現有手動實例化的風格
- 不改變 `StockRedisService` 等共用基礎設施的使用方式（它們屬於 `infrastructure/` 而非特定模組）
- 不重構 Auth 模組對 `UserRepository` 的依賴（Auth 模組使用自己的 Repository 不是跨模組問題）
- 不修改現有 `OrderCartAdapter`（它已經是理想的實作）

## Decisions

### 1. 命名慣例：Port + Adapter

採用 Port/Adapter 命名：
- **Port**（介面）：放在 `domain/ports.py`，命名為 `I{模組用途}Port`，例如 `IProductInfoPort`
- **Adapter**（實作）：放在 `infrastructure/adapters/`，命名為 `{目標模組}Adapter`，例如 `ProductInfoAdapter`

**為何不沿用 Repository 命名？** Port 與 Repository 的職責不同。Repository 是對持久化的抽象，Port 是對外部模組能力的抽象。使用 Port 命名能清楚區分「自己的資料存取」和「對其他模組的依賴」。

**替代方案：直接使用其他模組的 Domain 介面（如 `IProductRepository`）。** 這看似更簡單，但會讓模組依賴另一個模組的 Domain 層，而且通常只需要對方介面的部分方法，違反介面隔離原則（ISP）。

### 2. Cart 模組的 Product 依賴拆分為兩個 Port

Cart 模組對 Product 有兩種不同用途：
- **庫存校驗**（Use Case 層）：`AddToCartUseCase` / `UpdateCartItemQuantityUseCase` 需要 `get_by_id()` 查商品是否存在及庫存量
- **商品資訊富化**（Presentation 層）：`enrich_cart_items_with_product_info()` 需要查商品名稱、價格、圖片

合併為單一 Port `IProductInfoPort`，因為底層方法相同（`get_by_id`），只是呼叫方不同。Cart 模組定義自己的 Product 值物件（如 `ProductSnapshot`），避免直接依賴 Product 模組的 Entity。

### 3. Order 模組的 Product 依賴：重構 checkout.py 的 ProductModel 直接操作

`checkout.py` 目前直接 import `ProductModel` 做 `SELECT ... FOR UPDATE` 和修改 `stock_quantity`。這是最深層的耦合。

**方案：在 Order 的 Port 介面中定義 `get_products_for_checkout()` 和 `deduct_stock()` 方法**，將悲觀鎖和庫存扣減的邏輯封裝在 Adapter 中。CheckoutUseCase 只透過 Port 取得商品資訊和執行扣庫存，不再直接操作 ORM Model。

**替代方案：將 ProductModel 操作留在 checkout.py 中。** 雖然實務上可行（checkout 本來就需要 DB transaction），但這讓 Order 模組直接依賴 Product 模組的 ORM 層，未來 Product 的 Model 任何變動都會影響 Order。

### 4. Auth 模組的 Cart 依賴：單一 Port 封裝合併邏輯

Auth 只在登入時需要「合併訪客購物車到會員購物車」這單一操作。定義 `ICartMergePort` 介面，只暴露 `merge_guest_to_member(guest_token, user_id)` 方法，將 Cookie 解析、`CartMergeService` 的實例化全部封裝在 Adapter 中。

### 5. 現有 OrderCartAdapter 的調整

目前 `checkout` 路由直接實例化 `HybridCartRepository` 傳給 CheckoutUseCase。應改為使用現有的 `OrderCartAdapter`（或擴展它）來統一 cart 操作的入口，保持一致性。但 `OrderCartAdapter` 目前只封裝 `RedisCartRepository`，需要擴展支援 `HybridCartRepository`。

## Risks / Trade-offs

- **增加間接層** → Adapter 增加了程式碼量和間接呼叫。但每個 Adapter 都很薄（通常只是方法轉發），不會造成顯著的效能影響或認知負擔。
- **checkout 中的 DB transaction 跨 Adapter** → `OrderProductAdapter` 的 `get_products_for_checkout()` 和 `deduct_stock()` 需要共用同一個 DB session 才能維持事務一致性。Adapter 在建構時接收 `AsyncSession`，確保共用。[風險低]
- **重構範圍較大** → checkout.py 的改動最為複雜，因為需要將直接操作 ProductModel 的邏輯搬到 Adapter 中。需要仔細測試確保悲觀鎖和事務行為不變。→ 透過現有單元測試 + 手動測試結帳流程來驗證。
