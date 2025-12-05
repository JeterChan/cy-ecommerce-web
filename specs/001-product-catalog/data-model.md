# Data Model: Product Catalog

**Feature**: Product Catalog
**Last Updated**: 2025-12-03

## Conceptual Entities

### Product
Represents a single item available for sale.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique identifier (UUID or incremental ID) |
| name | string | Yes | Display name of the product |
| description | string | Yes | Detailed text description |
| price | number | Yes | Product price (integer or decimal) |
| imageUrl | string | Yes | URL to product image (placeholder if missing) |
| tags | string[] | No | List of tag names associated with the product |

### Tag
Represents a category or classification.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Unique name of the tag (e.g., "Electronics") |

## Frontend State Models (TypeScript Interfaces)

```typescript
// src/models/Product.ts

export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  imageUrl: string;
  tags: string[];
}

export interface ProductListResponse {
  products: Product[];
  total: number;
  page: number;
  limit: number;
}

export interface ProductSearchParams {
  query?: string;
  tag?: string;
  page?: number;
  limit?: number;
}
```
