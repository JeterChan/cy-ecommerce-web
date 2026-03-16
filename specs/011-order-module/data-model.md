# Data Model: Order Module

**Feature**: Order Module (011-order-module)
**Created**: 2026-02-21
**Status**: Draft

## 1. Domain Entities

### Order
Represents a customer's purchase record.

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Unique identifier for the order. |
| `user_id` | UUID | Identifier of the user who placed the order. |
| `total_amount` | Decimal | Total cost of the order (sum of items * quantity). |
| `status` | Enum | Current status (PENDING, PAID, SHIPPED, COMPLETED, CANCELLED). |
| `created_at` | DateTime | Timestamp when the order was created. |
| `updated_at` | DateTime | Timestamp when the order was last modified. |

### OrderItem
Represents a specific product within an order, capturing the price at the time of purchase.

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Unique identifier for the order item. |
| `order_id` | UUID | Foreign key to the parent Order. |
| `product_id` | UUID | Identifier of the product purchased. |
| `quantity` | Integer | Number of units purchased. |
| `price` | Decimal | Unit price at the time of purchase (Snapshot). |

## 2. Database Schema (PostgreSQL)

### Table: `orders`

```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
```

### Table: `order_items`

```sql
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price DECIMAL(10, 2) NOT NULL
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
```

## 3. Relationships

- **Order** (1) -> (N) **OrderItem**: An order can have multiple items.
- **Order** (N) -> (1) **User**: An order belongs to one user.
- **OrderItem** (N) -> (1) **Product**: An item refers to one product (though strictly speaking, we store `product_id`).

## 4. State Transitions (Order Status)

- **PENDING**: Initial state upon creation.
- **PAID**: Payment successful.
- **SHIPPED**: Items dispatched.
- **COMPLETED**: Order fulfilled/delivered.
- **CANCELLED**: Order voided (requires stock replenishment/refund logic, handled separately).

## 5. Validation Rules

- `quantity` must be greater than 0.
- `price` must be non-negative.
- `total_amount` must equal the sum of (`quantity` * `price`) for all items (unless explicitly overridden by discounts/shipping, which are out of scope for now).
- `user_id` must be valid.
