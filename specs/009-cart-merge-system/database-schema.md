# Cart 購物車資料庫結構說明

## 設計概述

購物車系統支援**會員購物車**和**訪客購物車**的雙重模式：
- **會員購物車**：持久化在 PostgreSQL，長期保存
- **訪客購物車**：儲存在 Redis（7天TTL），登入後可合併到會員購物車

---

## 資料表設計

### 1. `carts` 表 - 購物車

| 欄位 | 型別 | 說明 | 約束 |
|------|------|------|------|
| `id` | UUID | 主鍵 | PRIMARY KEY |
| `user_id` | UUID | 會員 ID（會員購物車） | FOREIGN KEY (users.id), NULLABLE, INDEX |
| `guest_token` | VARCHAR(255) | 訪客識別碼（訪客購物車暫存） | NULLABLE, INDEX |
| `created_at` | TIMESTAMP | 建立時間 | NOT NULL |
| `updated_at` | TIMESTAMP | 更新時間 | NOT NULL |

**約束條件**:
- ✅ `user_id` 和 `guest_token` **必須二選一**（不能同時為 NULL 或同時有值）
- ✅ `user_id` 部分唯一：每個會員只能有一個購物車（WHERE user_id IS NOT NULL）
- ✅ `guest_token` 部分唯一：每個訪客只能有一個購物車（WHERE guest_token IS NOT NULL）
- ✅ CASCADE DELETE：會員刪除時，購物車也刪除

**設計理由**:
1. **支援訪客購物車暫存**：訪客購物車主要在 Redis，但合併時需要暫時存入 DB
2. **防止重複**：同一擁有者（user_id 或 guest_token）只能有一個購物車
3. **互斥性**：確保一個購物車不會同時屬於會員和訪客

---

### 2. `cart_items` 表 - 購物車項目

| 欄位 | 型別 | 說明 | 約束 |
|------|------|------|------|
| `id` | UUID | 主鍵 | PRIMARY KEY |
| `cart_id` | UUID | 購物車 ID | FOREIGN KEY (carts.id), NOT NULL |
| `product_id` | UUID | 商品 ID | NOT NULL, INDEX |
| `price_snapshot` | NUMERIC(10,2) | 價格快照 | NOT NULL, CHECK (>= 0) |
| `quantity` | INTEGER | 數量 | NOT NULL, CHECK (> 0) |
| `created_at` | TIMESTAMP | 建立時間 | NOT NULL |
| `updated_at` | TIMESTAMP | 更新時間 | NOT NULL |

**約束條件**:
- ✅ `quantity > 0`：數量必須大於 0
- ✅ `price_snapshot >= 0`：價格必須大於等於 0
- ✅ UNIQUE (cart_id, product_id)：同一購物車不能有重複商品
- ✅ CASCADE DELETE：購物車刪除時，所有項目也刪除

**設計理由**:
1. **價格快照**：記錄商品加入購物車時的價格，防止價格變動影響總金額計算
2. **防止重複**：同一購物車的同一商品只能有一筆記錄（透過更新數量而非新增）
3. **user_id 不儲存**：透過 `cart_id` 關聯取得，符合正規化原則

---

## 關聯關係圖

```
┌──────────────────┐
│      users       │
│                  │
│  id (PK)         │
└────────┬─────────┘
         │ 1:1 (會員購物車)
         ▼
┌──────────────────────────────┐
│          carts               │
│                              │
│  id (PK)                     │
│  user_id (FK, NULLABLE)   ─┐ │
│  guest_token (NULLABLE)    │ │ ← 二選一（CHECK 約束）
└────────┬─────────────────────┘
         │ 1:N
         ▼
┌──────────────────────────────┐
│        cart_items            │
│                              │
│  id (PK)                     │
│  cart_id (FK)                │
│  product_id                  │
│  price_snapshot  ← 💰 價格快照│
│  quantity                    │
└──────────────────────────────┘
```

---

## 價格快照 (Price Snapshot) 設計

### 為什麼需要價格快照？

```
情境：使用者加入商品到購物車後，商品價格發生變動

時間點 1 (加入購物車):
  商品A 原價 $100 → 加入購物車

時間點 2 (商家調整價格):
  商品A 價格變更為 $120

時間點 3 (使用者結帳):
  - 若無價格快照：購物車顯示 $120（使用者困惑：我明明看到 $100）
  - 有價格快照：購物車顯示 $100（符合使用者預期）
```

### 價格快照的使用

```python
# 加入商品到購物車時
product = await get_product(product_id)
cart_item = CartItemModel(
    cart_id=cart.id,
    product_id=product.id,
    price_snapshot=product.price,  # 儲存當下價格
    quantity=2
)

# 計算購物車總金額
total = sum(item.price_snapshot * item.quantity for item in cart.items)
```

### 結帳時的價格處理

```python
# 結帳時應該檢查價格是否變動
for item in cart.items:
    current_price = await get_product_price(item.product_id)
    if current_price != item.price_snapshot:
        # 提示使用者價格已變動
        notify_price_change(item, current_price)
```

---

## 雙重識別設計

### 會員購物車

```sql
-- 會員 123 的購物車
INSERT INTO carts (id, user_id, guest_token)
VALUES ('cart-uuid-1', '123', NULL);

-- 查詢
SELECT * FROM carts WHERE user_id = '123';
```

### 訪客購物車（合併時暫存）

```sql
-- 訪客 guest_abc 的購物車（從 Redis 合併到 DB）
INSERT INTO carts (id, user_id, guest_token)
VALUES ('cart-uuid-2', NULL, 'guest_abc');

-- 查詢
SELECT * FROM carts WHERE guest_token = 'guest_abc';
```

---

## 防止重複商品

### 同一擁有者不能有重複商品

```sql
-- UNIQUE 索引確保同一購物車不能有重複商品
CREATE UNIQUE INDEX ix_cart_items_cart_product_unique 
ON cart_items(cart_id, product_id);

-- 範例：同一購物車加入相同商品會失敗
INSERT INTO cart_items (cart_id, product_id, quantity, price_snapshot)
VALUES ('cart-1', 'product-A', 2, 100.00);

-- ❌ 這會失敗（重複）
INSERT INTO cart_items (cart_id, product_id, quantity, price_snapshot)
VALUES ('cart-1', 'product-A', 3, 100.00);

-- ✅ 應該更新數量
UPDATE cart_items 
SET quantity = quantity + 3 
WHERE cart_id = 'cart-1' AND product_id = 'product-A';
```

---

## 使用情境

### 情境 1: 建立會員購物車

```python
# 1. 建立購物車
cart = CartModel(user_id=user_id, guest_token=None)
await session.add(cart)
await session.commit()

# 2. 新增商品（含價格快照）
product = await get_product(product_id)
item = CartItemModel(
    cart_id=cart.id,
    product_id=product.id,
    price_snapshot=product.price,
    quantity=2
)
await session.add(item)
await session.commit()
```

### 情境 2: 訪客購物車合併

```python
# 1. 從 Redis 取得訪客購物車
guest_items = await redis_repo.get_cart(guest_token)

# 2. 建立暫時的 DB 購物車（用於合併）
guest_cart = CartModel(user_id=None, guest_token=guest_token)
await session.add(guest_cart)

# 3. 將 Redis 資料寫入 DB
for item in guest_items:
    product = await get_product(item.product_id)
    db_item = CartItemModel(
        cart_id=guest_cart.id,
        product_id=item.product_id,
        price_snapshot=product.price,  # 重新取得當前價格
        quantity=item.quantity
    )
    await session.add(db_item)

# 4. 合併到會員購物車
member_cart = await get_member_cart(user_id)
for item in guest_cart.items:
    await merge_item_to_member_cart(member_cart, item)

# 5. 刪除訪客購物車（DB 和 Redis）
await session.delete(guest_cart)
await redis_repo.clear_cart(guest_token)
await session.commit()
```

### 情境 3: 查詢購物車總金額

```python
# 使用價格快照計算
cart = await session.get(CartModel, cart_id)
total = sum(
    item.price_snapshot * item.quantity 
    for item in cart.items
)

# 同時檢查價格變動
price_changes = []
for item in cart.items:
    current_price = await get_product_price(item.product_id)
    if current_price != item.price_snapshot:
        price_changes.append({
            "product_id": item.product_id,
            "old_price": item.price_snapshot,
            "new_price": current_price
        })

return {
    "total": total,
    "price_changes": price_changes  # 提示使用者價格已變動
}
```

---

## SQL Schema (參考)

```sql
-- carts 表
CREATE TABLE carts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    guest_token VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- 約束：user_id 和 guest_token 必須二選一
    CONSTRAINT ck_carts_owner_exclusivity 
        CHECK (
            (user_id IS NOT NULL AND guest_token IS NULL) OR 
            (user_id IS NULL AND guest_token IS NOT NULL)
        )
);

-- 部分唯一索引：每個會員只能有一個購物車
CREATE UNIQUE INDEX ix_carts_user_unique 
ON carts(user_id) 
WHERE user_id IS NOT NULL;

-- 部分唯一索引：每個訪客只能有一個購物車
CREATE UNIQUE INDEX ix_carts_guest_unique 
ON carts(guest_token) 
WHERE guest_token IS NOT NULL;

-- cart_items 表
CREATE TABLE cart_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_id UUID NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    product_id UUID NOT NULL,
    price_snapshot NUMERIC(10, 2) NOT NULL CHECK (price_snapshot >= 0),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- 同一購物車不能有重複商品
    UNIQUE (cart_id, product_id)
);

CREATE INDEX ix_cart_items_cart_id ON cart_items(cart_id);
CREATE INDEX ix_cart_items_product_id ON cart_items(product_id);
```

---

## Migration 指令

```bash
# 生成 migration
cd backend
alembic revision --autogenerate -m "Create carts and cart_items tables with price snapshot"

# 執行 migration
alembic upgrade head

# 檢查狀態
alembic current

# 驗證表結構
psql -d your_db -c "\d carts"
psql -d your_db -c "\d cart_items"
```

---

## 總結

✅ **已實現的需求**:
1. ✅ cart_items 儲存 **price_snapshot**（價格快照）
2. ✅ 支援**雙重識別**：user_id（會員）或 guest_token（訪客）
3. ✅ **防止重複**：同一擁有者的同一商品只能有一筆記錄

✅ **設計優勢**:
- 價格快照保護使用者體驗
- 支援訪客與會員購物車的統一管理
- 符合資料庫正規化原則
- 完整的約束條件確保資料完整性

下一步：執行 Alembic Migration 建立資料表！🚀

