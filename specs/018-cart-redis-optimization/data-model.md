# Data Model: Cart Redis Optimization (DDD Alignment)

## Entities

### 1. Product (PostgreSQL)
- **Table**: `products` (現有)
- **Key Fields**:
  - `id`: UUID
  - `price`: Decimal (真理來源)
  - `stock_quantity`: Integer (真理來源，用於 `FOR SHARE` 鎖定)

### 2. Cart Item (Redis Hash)
- **Key**: `cart:{owner_id}`
- **Fields**: `{product_id}`
- **Value**: JSON `{ "product_id": str, "quantity": int, "created_at": iso, "updated_at": iso }`
- **Note**: `RedisCartRepository` 已實作此結構。

## State Transitions & Validation

### Add to Cart (AddToCartUseCase)
1. **DB Lock**: `SELECT stock_quantity FROM products WHERE id = :id FOR SHARE` (透過 `ProductRepository.get_by_id_with_lock`)。
2. **Business Rule**: `new_quantity <= stock_quantity`。
3. **Storage Update**: `CartRepository.add_item` 更新 Redis。
4. **Consistency**: 確保在資料庫事務內進行庫存鎖定，隨後更新 Redis。

### View Cart (GetCartUseCase + enrich_cart_items_with_product_info)
1. **Fetch IDs**: `CartRepository.get_cart` 獲取所有商品 ID 與數量。
2. **Fetch Values**: `ProductRepository.get_by_id` 獲取最新價格與名稱。
3. **Merge**: 計算 `subtotal` 並返回 `CartItemResponse`。
