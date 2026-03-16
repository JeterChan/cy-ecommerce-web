# 資料模型：商品管理模組 (Product Management Module)

**功能**: 商品管理模組
**日期**: 2026-02-12
**狀態**: 設計中

## 實體 (Entities)

### Product (領域實體)

代表可販售項目的核心商業物件。

| 屬性 | 類型 | 必填 | 描述 | 限制 |
|---|---|---|---|---|
| `id` | UUID | 是 | 唯一識別碼 | Primary Key |
| `name` | String | 是 | 商品名稱 | Max 255 chars |
| `description` | Text | 否 | 詳細描述 | |
| `price` | Decimal | 是 | 商品價格 | >= 0 |
| `stock_quantity` | Integer | 是 | 庫存數量 | >= 0 |
| `is_active` | Boolean | 是 | 可見狀態 | 預設: True |
| `image_url` | String | 否 | 商品圖片 URL | 有效的 URL 格式 |
| `created_at` | DateTime | 是 | 建立時間戳記 | 自動生成 |
| `updated_at` | DateTime | 是 | 最後更新時間戳記 | 自動生成 |

### Category (領域實體)

代表商品的分類群組。

| 屬性 | 類型 | 必填 | 描述 | 限制 |
|---|---|---|---|---|
| `id` | UUID | 是 | 唯一識別碼 | Primary Key |
| `name` | String | 是 | 分類名稱 | 唯一, Max 100 chars |
| `slug` | String | 是 | URL 友善識別碼 | 唯一, 僅限英數字與連字號 |
| `parent_id` | UUID | 否 | 父分類 ID | 自參照 FK (選填) |

### Product-Category Association (商品-分類關聯)

代表商品與分類之間的多對多關係。

| 屬性 | 類型 | 必填 | 描述 | 限制 |
|---|---|---|---|---|
| `product_id` | UUID | 是 | 參照至 Product | FK |
| `category_id` | UUID | 是 | 參照至 Category | FK |

## API 合約 (OpenAPI 風格)

### Products (商品)

- `GET /api/v1/products`
  - 查詢參數: `page`, `limit`, `category_id`, `search`
  - 回應: `200 OK` (List[Product])

- `GET /api/v1/products/{id}`
  - 回應: `200 OK` (Product), `404 Not Found`

- `POST /api/v1/products` (限管理員)
  - Body: `ProductCreateSchema`
  - 回應: `201 Created` (Product), `400 Bad Request`

- `PUT /api/v1/products/{id}` (限管理員)
  - Body: `ProductUpdateSchema`
  - 回應: `200 OK` (Product), `404 Not Found`

- `DELETE /api/v1/products/{id}` (限管理員)
  - 回應: `204 No Content`, `404 Not Found`

### Categories (分類)

- `GET /api/v1/categories`
  - 回應: `200 OK` (List[Category])

- `POST /api/v1/categories` (限管理員)
  - Body: `CategoryCreateSchema`
  - 回應: `201 Created` (Category), `400 Bad Request`

- `PUT /api/v1/categories/{id}` (限管理員)
  - Body: `CategoryUpdateSchema`
  - 回應: `200 OK` (Category), `404 Not Found`

- `DELETE /api/v1/categories/{id}` (限管理員)
  - 回應: `204 No Content`, `404 Not Found`

## 實作細節 (Clean Architecture)

**Domain Layer (`modules/product/domain/`)**:
- `entities.py`: `Product`, `Category` (用於領域邏輯的 Pure Python 類別/Pydantic 模型)。
- `repository.py`: `ProductRepository`, `CategoryRepository` (抽象介面)。

**Infrastructure Layer (`modules/product/infrastructure/`)**:
- `models.py`: SQLAlchemy ORM 定義 (`ProductModel`, `CategoryModel`)。
- `repositories/`: 實作介面的 `SqlAlchemyProductRepository`, `SqlAlchemyCategoryRepository`。

**Use Cases Layer (`modules/product/use_cases/`)**:
- `create_product.py`, `get_product_list.py`, 等等。

**API Layer (`modules/product/api/`)**:
- `v1/routes.py`: 將 HTTP 請求映射到 Use Cases 的 FastAPI 路由器。