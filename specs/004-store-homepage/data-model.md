# Data Model: Store Homepage

## Entities

### Product (Existing Update)
*Extends existing Product interface*

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `name` | string | Product name |
| `price` | number | Unit price |
| `tags` | string[] | Used as Categories |
| `is_featured` | boolean | **New**: Indicates if product is a seasonal feature |
| ... | ... | Other existing fields |

### Promotion (New)
*Represents the current marketing offer*

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Short title (e.g., "滿額優惠") |
| `description` | string | Full text (e.g., "消費滿 10,000 打 95 折") |
| `threshold` | number | Spending amount required |
| `discount_rate` | number | Multiplier (e.g., 0.95) |

### Category (Derived)
*Derived from Product Tags*

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | The tag name (e.g., "3C") |
| `count` | number | (Optional) Number of items |

## Stores / State

### ProductStore (or use Service directly)
- `featuredProducts`: Array<Product>
- `categories`: Array<string>

### PromotionStore (Optional)
- `currentPromotion`: Promotion
