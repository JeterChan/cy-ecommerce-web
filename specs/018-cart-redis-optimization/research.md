# Research: Cart Redis Optimization (DDD Alignment)

## Decisions

### 1. Integration with Existing DDD Structure
- **Decision**: 保持現有的 `modules/cart` 架構，並在 `AddToCartUseCase` 中引入對 `IProductRepository` 的依賴。
- **Rationale**: 庫存檢查屬於業務邏輯，應在 Application 層（Use Case）處理，而非 Presentation 層（Routes）。注入 Repository 符合依賴倒置原則。

### 2. Cross-Module Dependency
- **Decision**: `AddToCartUseCase` 將透過構造函數接收 `ICartRepository` 與 `IProductRepository`。
- **Flow**:
  1. `AddToCartUseCase` 調用 `ProductRepository.get_by_id(product_id)`（需實作支援 `FOR SHARE` 鎖定的版本）。
  2. 檢查 `existing_stock` 是否充足。
  3. 若充足，調用 `CartRepository.add_item` 更新 Redis。
- **Rationale**: 這樣可以確保庫存檢查與加入購物車的邏輯封裝在一個原子性的業務操作中。

### 3. Database Locking Implementation
- **Decision**: 在 `SqlAlchemyProductRepository` 中增加 `get_by_id_with_lock` 方法，使用 `with_for_update(read=True)` (即 `FOR SHARE`)。
- **Rationale**: `FOR SHARE` 允許其他事務讀取但禁止修改，適合用於「讀取後驗證並寫入另一個存儲（Redis）」的場景，防止校驗期間庫存被修改。

### 4. Response Enrichment
- **Decision**: 保持現有的 `enrich_cart_items_with_product_info` 機制用於 `GET /cart`。
- **Rationale**: 該機制已能滿足動態撈取最新價格的需求，無需重複開發。

## Alternatives Considered

### Alternative: Orchestration Service
- **Rejected Because**: 目前邏輯尚不複雜，直接在 Use Case 中組合兩個 Repository 較為簡潔。若未來涉及更多模組（如促銷、會員等級），再考慮引入 Orchestration Service。

### Alternative: Checking stock in Routes.py
- **Rejected Because**: 違反 DDD 原則。路由層應僅負責請求解析與響應封裝，不應包含「檢查庫存並決定是否加入購物車」的業務規則。
