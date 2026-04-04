## ADDED Requirements

### Requirement: Cart 模組定義 IProductInfoPort 介面
Cart 模組 **SHALL** 在 `domain/ports.py` 定義 `IProductInfoPort` 抽象介面，作為對 Product 模組能力的唯一依賴入口。此介面 **MUST** 包含 Cart 模組所需的商品查詢方法，且回傳 Cart 模組自己定義的值物件（如 `ProductSnapshot`），不依賴 Product 模組的 Entity。

#### Scenario: Use Case 透過 Port 查詢商品庫存
- **WHEN** `AddToCartUseCase` 或 `UpdateCartItemQuantityUseCase` 需要查詢商品是否存在及庫存量
- **THEN** **MUST** 透過 `IProductInfoPort.get_product_info(product_id)` 取得商品資訊
- **AND** 不得直接 import `IProductRepository` 或 `SqlAlchemyProductRepository`

#### Scenario: Presentation 層透過 Port 進行商品資訊富化
- **WHEN** Cart 路由需要為購物車項目附加商品名稱、價格、圖片等資訊
- **THEN** **MUST** 透過 `IProductInfoPort` 取得商品詳情
- **AND** 不得直接 import `SqlAlchemyProductRepository`

### Requirement: Cart 模組提供 ProductInfoAdapter 實作
Cart 模組 **SHALL** 在 `infrastructure/adapters/product_info_adapter.py` 提供 `ProductInfoAdapter` 類別，實作 `IProductInfoPort` 介面，內部橋接 Product 模組的 `SqlAlchemyProductRepository`。

#### Scenario: Adapter 正確橋接 Product 模組
- **WHEN** `ProductInfoAdapter` 被實例化並呼叫 `get_product_info(product_id)`
- **THEN** **MUST** 委派給 `SqlAlchemyProductRepository.get_by_id()` 並將結果轉換為 Cart 模組的值物件

### Requirement: Order 模組定義 IProductPort 介面
Order 模組 **SHALL** 在 `domain/ports.py` 定義 `IProductPort` 抽象介面，封裝結帳、取消訂單等場景所需的商品操作。此介面 **MUST** 包含悲觀鎖取得商品、扣減庫存、回補庫存等方法。

#### Scenario: Checkout Use Case 透過 Port 操作商品
- **WHEN** `CheckoutUseCase` 需要取得商品並扣減庫存
- **THEN** **MUST** 透過 `IProductPort` 的方法執行
- **AND** 不得直接 import `ProductModel` 或 `SqlAlchemyProductRepository`

#### Scenario: UpdateOrderStatus Use Case 透過 Port 回補庫存
- **WHEN** `UpdateOrderStatusUseCase` 取消訂單需要回補庫存
- **THEN** **MUST** 透過 `IProductPort.restore_stock(product_id, quantity)` 執行
- **AND** 不得直接 import `IProductRepository`

### Requirement: Order 模組提供 OrderProductAdapter 實作
Order 模組 **SHALL** 在 `infrastructure/adapters/order_product_adapter.py` 提供 `OrderProductAdapter` 類別，實作 `IProductPort` 介面，內部橋接 Product 模組的具體實作。

#### Scenario: Adapter 封裝悲觀鎖商品查詢
- **WHEN** `OrderProductAdapter.get_products_for_checkout(product_ids)` 被呼叫
- **THEN** **MUST** 執行 `SELECT ... FOR UPDATE` 悲觀鎖查詢，按 ID 排序防止死鎖
- **AND** 回傳 Order 模組定義的商品值物件列表

#### Scenario: Adapter 封裝庫存扣減
- **WHEN** `OrderProductAdapter.deduct_stock(product_id, quantity)` 被呼叫
- **THEN** **MUST** 在現有 DB session 的事務內扣減商品庫存

### Requirement: Auth 模組定義 ICartMergePort 介面
Auth 模組 **SHALL** 在 `domain/ports.py` 定義 `ICartMergePort` 抽象介面，封裝登入時合併訪客購物車的操作。

#### Scenario: 登入路由透過 Port 執行購物車合併
- **WHEN** 使用者登入且存在訪客購物車 Token
- **THEN** **MUST** 透過 `ICartMergePort.merge_guest_cart(request, user_id)` 執行合併
- **AND** 不得直接 import `CartMergeService` 或 `get_guest_token_from_cookie`

### Requirement: Auth 模組提供 CartMergeAdapter 實作
Auth 模組 **SHALL** 在 `infrastructure/adapters/cart_merge_adapter.py` 提供 `CartMergeAdapter` 類別，實作 `ICartMergePort` 介面，內部橋接 Cart 模組的 `CartMergeService` 和 `get_guest_token_from_cookie`。

#### Scenario: Adapter 正確橋接 Cart 模組的合併邏輯
- **WHEN** `CartMergeAdapter.merge_guest_cart(request, user_id)` 被呼叫
- **THEN** **MUST** 從 Request 中提取 guest token（透過 `get_guest_token_from_cookie`）
- **AND** 若 token 存在，**MUST** 呼叫 `CartMergeService.merge_guest_to_member()`

### Requirement: Order 模組擴展 OrderCartAdapter 支援 HybridCartRepository
Order 模組的 `OrderCartAdapter` **SHALL** 支援接受 `HybridCartRepository` 作為底層實作，使 checkout 路由不再需要直接 import `HybridCartRepository`。

#### Scenario: Checkout 路由使用 OrderCartAdapter
- **WHEN** checkout 路由需要實例化購物車相關依賴
- **THEN** **MUST** 透過 `OrderCartAdapter` 封裝 `HybridCartRepository`
- **AND** 不得直接 import `HybridCartRepository`

### Requirement: 模組間 import 隔離規則
每個模組的 Presentation 層和 Application 層 **SHALL NOT** 直接 import 其他模組的 Infrastructure 層類別。跨模組依賴 **MUST** 透過本模組 Domain 層定義的 Port 介面進行。

#### Scenario: Cart 模組不直接 import Product Infrastructure
- **WHEN** 檢查 Cart 模組的 `presentation/` 和 `application/` 目錄下所有 Python 檔案
- **THEN** 不得出現 `from modules.product.infrastructure` 開頭的 import 語句

#### Scenario: Order 模組不直接 import Product Infrastructure
- **WHEN** 檢查 Order 模組的 `presentation/` 和 `application/` 目錄下所有 Python 檔案
- **THEN** 不得出現 `from modules.product.infrastructure` 開頭的 import 語句

#### Scenario: Auth 模組不直接 import Cart Infrastructure
- **WHEN** 檢查 Auth 模組的 `presentation/` 和 `application/` 目錄下所有 Python 檔案
- **THEN** 不得出現 `from modules.cart.infrastructure` 開頭的 import 語句

#### Scenario: Order 模組不直接 import Cart Infrastructure
- **WHEN** 檢查 Order 模組的 `presentation/` 和 `application/` 目錄下所有 Python 檔案
- **THEN** 不得出現 `from modules.cart.infrastructure` 開頭的 import 語句
