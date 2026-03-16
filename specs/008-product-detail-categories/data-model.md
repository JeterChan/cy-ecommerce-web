# Data Model: Product & Category

**Feature**: `008-product-detail-categories`

## Entities

### Category

Represents a hierarchical grouping of products.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique identifier (UUID or slug-like) |
| `name` | `string` | Display name (e.g., "Smartphones") |
| `parentId` | `string` (Optional) | ID of the parent category. `null` if root. |
| `slug` | `string` | URL-friendly identifier |

### Product (Update)

Existing entity, updated to link to Category.

| Field | Type | Description |
|-------|------|-------------|
| ... | ... | Existing fields |
| `categoryId` | `string` | **NEW**: Foreign key to the primary `Category`. |

## Relationships

- **Category (1) -- (*) Category**: Self-referencing hierarchy (Parent/Child).
- **Category (1) -- (*) Product**: One category contains many products. (For this MVP, a product belongs to one primary category).
