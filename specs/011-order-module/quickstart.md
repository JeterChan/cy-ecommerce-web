# Quickstart: Order Module

**Feature**: Order Module (011-order-module)
**Created**: 2026-02-21

## Prerequisites

- Python 3.12+
- Docker & Docker Compose
- PostgreSQL (running locally or in Docker)
- Redis (running locally or in Docker)

## Setup

1.  **Environment Variables**:
    Ensure `.env` contains:
    ```bash
    DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce_db
    REDIS_URL=redis://localhost:6379/0
    ```

2.  **Install Dependencies**:
    ```bash
    cd backend
    pip install -r requirements.txt
    ```

## Database Migration

The Order module introduces new tables (`orders`, `order_items`).

1.  **Generate Migration**:
    ```bash
    cd backend
    alembic revision --autogenerate -m "create_order_tables"
    ```

2.  **Apply Migration**:
    ```bash
    alembic upgrade head
    ```

## Running Tests

1.  **Unit Tests**:
    ```bash
    cd backend
    pytest tests/unit/modules/order
    ```

2.  **Integration Tests**:
    ```bash
    cd backend
    pytest tests/integration/modules/order
    ```

## Verification Steps (Manual)

1.  **Start API**:
    ```bash
    uvicorn src.main:app --reload
    ```

2.  **Add Item to Cart** (via existing Cart API):
    ```bash
    curl -X POST http://localhost:8000/api/v1/cart/items \
      -H "Content-Type: application/json" \
      -d '{"product_id": "uuid-of-product", "quantity": 1}'
    ```

3.  **Create Order**:
    ```bash
    curl -X POST http://localhost:8000/api/v1/orders \
      -H "Content-Type: application/json" \
      -d '{"user_id": "uuid-of-user"}'
    ```
    - *Expected*: 201 Created, returns Order ID.

4.  **Verify Cart Cleared**:
    ```bash
    curl -X GET http://localhost:8000/api/v1/cart
    ```
    - *Expected*: Empty list.

5.  **Get Order Details**:
    ```bash
    curl -X GET http://localhost:8000/api/v1/orders/{order_id}
    ```
    - *Expected*: Returns order details with snapshot price.
