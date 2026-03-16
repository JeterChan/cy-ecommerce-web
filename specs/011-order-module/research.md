# Research: Order Module Implementation

**Feature**: Order Module (011-order-module)
**Created**: 2026-02-21
**Status**: Researching

## 1. Clean Architecture in FastAPI

**Decision**: Adopt a standard 4-layer Clean Architecture.

**Rationale**:
- **Separation of Concerns**: Decouples business logic from frameworks (FastAPI) and external agents (DB, Redis).
- **Testability**: Domain logic can be tested without spinning up a server or DB.
- **Maintainability**: Clear boundaries make it easier to navigate and modify code.

**Structure**:
1.  **Domain Layer** (`src/modules/order/domain`):
    -   Entities (`Order`, `OrderItem` models - pure Python objects, not SQLAlchemy models).
    -   Value Objects (`OrderStatus`, `Money`).
    -   Repository Interfaces (Abstract Base Classes).
2.  **Use Case Layer** (`src/modules/order/application` or `use_cases`):
    -   Application logic (e.g., `CreateOrderUseCase`, `GetOrderUseCase`).
    -   Orchestrates data flow between repositories and domain entities.
    -   Handles transactions and business rules (e.g., check stock, calculate total).
3.  **Infrastructure Layer** (`src/modules/order/infrastructure`):
    -   Database implementation (SQLAlchemy models, Repository implementations).
    -   Redis implementation (Cache repositories).
    -   External services adapters (if any).
4.  **Presentation/Interface Layer** (`src/modules/order/presentation` or `api`):
    -   FastAPI routers (`endpoints`).
    -   DTOs (Pydantic models for Request/Response).

## 2. Database Schema & Price Snapshot

**Decision**: Use PostgreSQL with `orders` and `order_items` tables. `order_items` MUST store the `price` at the time of purchase.

**Rationale**:
- **Data Integrity**: Prices change over time. Historical orders must reflect the amount actually paid.
- **Relational Integrity**: PostgreSQL ensures ACID compliance, which is critical for financial transactions.

**Schema Design**:
- `orders`: `id` (UUID), `user_id`, `total_amount`, `status`, `created_at`, `updated_at`.
- `order_items`: `id`, `order_id`, `product_id`, `quantity`, `price` (The snapshot).

## 3. Transaction Management

**Decision**: Use SQLAlchemy `Session` with atomic transactions for Order Creation.

**Rationale**:
- **Atomicity**: "Create Order" + "Create Order Items" + "Clear Cart" (+ "Deduct Stock") must happen all together or not at all.
- **Consistency**: Prevents "Ghost Orders" (money paid but no order) or "Free Items" (order created but cart not cleared).

**Implementation**:
- The `CreateOrderUseCase` should manage the transaction scope (Unit of Work pattern).
- If any step fails (e.g., clearing cart in Redis fails, or DB insert fails), the entire operation rolls back.

## 4. Redis Usage

**Decision**: Use Redis for:
1.  **Shopping Cart Retrieval**: The order module needs to read the *current* cart to create the order.
2.  **Cart Clearing**: After successful order persistence, the cart in Redis must be deleted.
3.  **(Optional) Idempotency Key**: Store a key (e.g., `order_idempotency:{user_id}:{hash}`) to prevent double submissions.

**Clarification on "Cache Price"**:
- The user requirement "在使用者要結帳時，將商品價格快取儲存" is interpreted as **Persisting the Price Snapshot in the Database**.
- While Redis *can* cache prices, the critical "storage" for an Order is the permanent DB record. We will rely on the DB `order_items.price` column for this.

## 5. Technology Stack Alignment

- **Language**: Python 3.12 (Matches project constraint).
- **Framework**: FastAPI (Matches project constraint).
- **Database**: PostgreSQL (Matches project constraint).
- **Cache**: Redis (Matches project constraint).
