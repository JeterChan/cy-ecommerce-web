# Frontend Data Contracts

**Feature**: `008-product-detail-categories`

## TypeScript Interfaces

### `Category`

```typescript
export interface Category {
  id: string;
  name: string;
  parentId?: string; // Optional for root categories
  slug: string;
}
```

### `Product` (Updated)

```typescript
export interface Product {
  // ... existing fields
  categoryId?: string; // Link to the primary category
}
```

## Service Contracts (`CategoryService`)

### `getTree()`

Returns a list of categories. The consumer (Component) is responsible for building the tree structure if needed, or the service can return a nested structure. For simplicity in MVP:

```typescript
// Returns flat list, UI handles hierarchy rendering
async function getCategories(): Promise<Category[]>;
```

### `getById(id)`

```typescript
async function getCategoryById(id: string): Promise<Category | undefined>;
```
