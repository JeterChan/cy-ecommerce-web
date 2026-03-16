# Quickstart: Order Checkout and Management System

## 1. 結帳 (Checkout)
使用者將商品加入購物車後，呼叫此 API 進行結帳。

**Endpoint**: `POST /api/v1/orders/checkout`

**Payload**:
```json
{
  "recipient_name": "張三",
  "recipient_phone": "0912345678",
  "shipping_address": "台北市信義區信義路五段7號",
  "payment_method": "COD"
}
```

**成功回應 (201 Created)**:
```json
{
  "id": "uuid-order-id",
  "status": "PROCESSING",
  "total_amount": 1500.0,
  "created_at": "2026-03-15T10:00:00Z",
  "items": [
    {
      "product_id": "uuid-product-1",
      "product_name": "高級耳機",
      "price": 1500.0,
      "quantity": 1
    }
  ]
}
```

## 2. 查看個人訂單歷史 (List Orders)
**Endpoint**: `GET /api/v1/orders`

**成功回應 (200 OK)**:
```json
[
  {
    "id": "uuid-order-id",
    "status": "PROCESSING",
    "total_amount": 1500.0,
    "created_at": "2026-03-15T10:00:00Z"
  }
]
```

## 3. 查看訂單詳情 (Order Details)
**Endpoint**: `GET /api/v1/orders/{order_id}`

## 4. 異常處理
- **400 Bad Request**: 
    - `{"detail": "Insufficient stock for product X"}`
    - `{"detail": "Price changed for product Y. Please refresh."}`
- **404 Not Found**: 
    - `{"detail": "Cart is empty"}`
