# Data Model: Order Frontend

## Core Entities

### Order (List View)
Represents a summary of an order for list display.

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | UUID | Unique identifier |
| `user_id` | String | ID of the user who placed the order |
| `created_at` | ISO8601 | Order placement date |
| `total_amount` | Number | Total price of the order |
| `status` | Enum | Current status (PENDING, PAID, SHIPPED, COMPLETED, CANCELLED) |
| `shipping_fee` | Number | Shipping cost included in total |

### OrderDetail (Full View)
Extends `Order` with comprehensive details.

| Field | Type | Description |
| :--- | :--- | :--- |
| `items` | Array<OrderItem> | List of products in the order |
| `purchaser_info` | PurchaserInfo | Information about the buyer (name, email, phone) |
| `shipping_info` | ShippingInfo | Delivery details (recipient, address, method) |
| `payment_info` | PaymentInfo | Payment details (method, status, transaction ID) |
| `note` | String (Optional) | User's note for the order |

### OrderItem
Represents a line item in an order.

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | UUID | Unique identifier for the item |
| `product_id` | String | Reference to the product |
| `product_name` | String | Name of the product at purchase time |
| `quantity` | Number | Quantity purchased |
| `unit_price` | Number | Price per unit at purchase time |
| `subtotal` | Number | `quantity * unit_price` |
| `options` | JSON (Optional) | Selected product options (color, size, etc.) |

### ShippingInfo
| Field | Type | Description |
| :--- | :--- | :--- |
| `recipient_name` | String | Name of the person receiving the package |
| `recipient_phone` | String | Contact phone number |
| `method` | Enum | HOME_DELIVERY, STORE_PICKUP_711 |
| `address` | String | Delivery address (if HOME_DELIVERY) |
| `store_name` | String | Name of the pickup store (if STORE_PICKUP_711) |
| `tracking_number` | String (Optional) | Shipping tracking code |

### PaymentInfo
| Field | Type | Description |
| :--- | :--- | :--- |
| `method` | Enum | CREDIT_CARD, COD, ATM |
| `status` | Enum | UNPAID, PAID, FAILED, REFUNDED |
| `transaction_id` | String (Optional) | External payment gateway transaction ID |

## Relationships

- **User** -> 1:N -> **Order**
- **Order** -> 1:N -> **OrderItem**
- **Order** -> 1:1 -> **ShippingInfo**
- **Order** -> 1:1 -> **PaymentInfo**
