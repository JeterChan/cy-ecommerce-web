# Data Model: Shopping Cart

**Feature**: Shopping Cart
**Last Updated**: 2025-12-03

## Conceptual Entities

### CartItem
Represents a product added to the cart.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| productId | string | Yes | Reference to the Product ID |
| name | string | Yes | Snapshot of product name |
| price | number | Yes | Snapshot of product price |
| imageUrl | string | Yes | Snapshot of product image |
| quantity | number | Yes | Quantity selected (min 1) |

### Cart (Store State)
The global state for the shopping cart.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| items | CartItem[] | Yes | List of items in the cart |

## Frontend State Models (TypeScript Interfaces)

```typescript
// src/models/Cart.ts

export interface CartItem {
  productId: string;
  name: string;
  price: number;
  imageUrl: string;
  quantity: number;
}

export interface CartState {
  items: CartItem[];
}

// Pinia Store Interface
export interface CartStore {
  items: CartItem[];
  totalQuantity: number; // Derived
  totalAmount: number;   // Derived
  addToCart: (product: Product, quantity: number) => void;
  removeFromCart: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
}
```
