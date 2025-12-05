# Data Model: 建立訂單流程

**Feature**: 003-checkout-flow
**Version**: 1.0.0

## Entities

### Order (訂單)

代表一筆成立的交易。

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| id | UUID | Yes | Unique Identifier | |
| user_id | UUID | Yes | ID of the purchaser (if logged in) or guest ID | |
| status | Enum | Yes | Order status | PENDING, PAID, SHIPPED, COMPLETED, CANCELLED |
| total_amount | Decimal | Yes | Total transaction amount | >= 0 |
| shipping_fee | Decimal | Yes | Cost of shipping | >= 0 |
| note | String | No | User's note | Max 500 chars |
| created_at | DateTime | Yes | Timestamp of creation | |
| updated_at | DateTime | Yes | Timestamp of last update | |

### OrderItem (訂單細項)

訂單中的商品明細。

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| id | UUID | Yes | Unique Identifier | |
| order_id | UUID | Yes | Foreign Key to Order | |
| product_id | UUID | Yes | Foreign Key to Product | |
| product_name | String | Yes | Snapshot of product name | |
| quantity | Integer | Yes | Quantity purchased | > 0 |
| unit_price | Decimal | Yes | Price per unit at purchase time | >= 0 |
| subtotal | Decimal | Yes | quantity * unit_price | >= 0 |

### ShippingInfo (收件資訊)

訂單的運送與收件人資料。

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| order_id | UUID | Yes | Foreign Key to Order (1:1) | |
| recipient_name | String | Yes | Name of recipient | |
| recipient_phone | String | Yes | Phone of recipient | Valid phone format |
| shipping_method | Enum | Yes | Delivery method | HOME_DELIVERY, STORE_PICKUP_711 |
| address | String | No | Delivery address | Required if method is HOME_DELIVERY |
| store_id | String | No | Convenience store ID | Required if method is STORE_PICKUP_711 |
| store_name | String | No | Convenience store name | Required if method is STORE_PICKUP_711 |

### PurchaserInfo (購買人資訊)

購買者的聯絡資料（可能與收件人不同）。

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| order_id | UUID | Yes | Foreign Key to Order (1:1) | |
| name | String | Yes | Purchaser's name | |
| phone | String | Yes | Purchaser's phone | Valid phone format |
| email | String | Yes | Purchaser's email | Valid email format |

### PaymentInfo (付款資訊)

訂單的付款狀態與方式。

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| order_id | UUID | Yes | Foreign Key to Order (1:1) | |
| method | Enum | Yes | Payment method | CREDIT_CARD, ATM, COD |
| status | Enum | Yes | Payment status | UNPAID, PAID, FAILED, REFUNDED |
| transaction_id | String | No | External gateway transaction ID | |
| paid_at | DateTime | No | Timestamp of payment | |

## Relationships

- **Order** has_many **OrderItem**
- **Order** has_one **ShippingInfo**
- **Order** has_one **PurchaserInfo**
- **Order** has_one **PaymentInfo**
