# Data Model: Product Management Enhancement

## Entities

### User (更新)
在現有 `User` 模型中新增角色屬性。

- **role**: 字串 (Enum)
    - 值: `user`, `admin`
    - 預設: `user`

### Product (更新)
調整與 `ProductImage` 的關聯。

- **images**: 關聯屬性 (One-to-Many)
    - 連結到 `ProductImage` 列表。

### ProductImage (新)
儲存商品的複數圖片。

- **id**: UUID (主鍵)
- **product_id**: UUID (外鍵，關聯至 `Product`)
- **url**: 字串 (S3 圖片位址)
- **alt_text**: 字串 (圖片替代文字，選填)
- **is_primary**: 布林值 (是否為主圖/封面圖)
    - 每件商品應至少有一張主圖。

## Validation Rules

- **商品圖片上限**: 每個商品最多關聯 5 張圖片。
- **主圖唯一性**: 每個商品必須且僅能有一張圖片標記為 `is_primary=true`。
- **庫存非負**: `stock_quantity` 必須大於等於 0。

## State Transitions

### 商品上架狀態 (is_active)
- `true`: 前台可見，可購買（若有庫存）。
- `false`: 前台不可見（或僅限管理員），不可購買。

### 庫存狀態 (即時計算)
- **庫存充足**: `stock_quantity >= 5`
- **庫存緊張 (Low Stock)**: `0 < stock_quantity < 5`
- **已售罄 (Out of Stock)**: `stock_quantity == 0`
