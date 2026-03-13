# Implementation Plan - Order Module

**Feature**: Order Module (011-order-module)
**Status**: Planned
**Spec**: [spec.md](./spec.md)

## Technical Context

- **Language**: Python 3.12 (Constraint)
- **Framework**: FastAPI (Constraint)
- **Database**: PostgreSQL (Constraint) - `orders`, `order_items`
- **Cache**: Redis (Constraint) - Cart retrieval, clearing
- **Architecture**: Clean Architecture (Constraint)
- **Location**: `backend/src/modules/order`

## Constitution Check

- [x] **High Quality**: Using Clean Architecture to ensure separation of concerns and maintainability.
- [x] **Testability**: Domain logic isolated from infrastructure; Unit tests for Use Cases; Integration tests for Repositories and APIs.
- [x] **MVP First**: Focusing on core flow (Create Order, Clear Cart, Snapshot Price) without complex features like discounts or shipping calculation initially.
- [x] **Avoid Overdesign**: Standard relational schema; using Redis only for existing cart data and potential idempotency.
- [x] **Traditional Chinese First**: Documentation and comments will primarily use Traditional Chinese.

## Gates

- [x] **Requirements Clear**: Spec is detailed.
- [x] **Tech Stack Defined**: Python 3.12, FastAPI, PG, Redis.
- [x] **Design Complete**: Data model and API contract defined.

## Phase 1: Design & Documentation (Completed)

- [x] **Research**: [research.md](./research.md)
- [x] **Data Model**: [data-model.md](./data-model.md)
- [x] **API Contract**: [contracts/openapi.yaml](./contracts/openapi.yaml)
- [x] **Quickstart**: [quickstart.md](./quickstart.md)

## Phase 2: Core Implementation (Backend)

### 2.1 Domain Layer
- **Goal**: Define business entities and rules.
- **Files**:
    - `src/modules/order/domain/entities.py` (Order, OrderItem)
    - `src/modules/order/domain/repositories.py` (Abstract Interfaces)
    - `src/modules/order/domain/value_objects.py` (OrderStatus)

### 2.2 Infrastructure Layer (Database)
- **Goal**: Implement persistence.
- **Files**:
    - `src/modules/order/infrastructure/models.py` (SQLAlchemy Models)
    - `src/modules/order/infrastructure/repositories/postgres_order_repository.py`
    - `src/modules/order/infrastructure/migrations/` (Alembic)

### 2.3 Infrastructure Layer (Cart Integration)
- **Goal**: Interact with Cart module (Redis).
- **Files**:
    - `src/modules/order/infrastructure/repositories/redis_cart_repository.py` (To fetch/clear cart)

### 2.4 Application Layer (Use Cases)
- **Goal**: Implement business logic flows.
- **Files**:
    - `src/modules/order/application/use_cases/create_order.py` (Transaction management, snapshotting)
    - `src/modules/order/application/use_cases/get_order.py`
    - `src/modules/order/application/use_cases/list_orders.py`
    - `src/modules/order/application/dtos/inputs.py` (Request DTOs)
    - `src/modules/order/application/dtos/outputs.py` (Response DTOs)

### 2.5 Presentation Layer (API)
- **Goal**: Expose functionality via HTTP.
- **Files**:
    - `src/modules/order/presentation/routes.py`
    - `src/main.py` (Register router)

## Phase 3: Testing & Verification

- **Goal**: Ensure correctness.
- **Tasks**:
    - Write Unit Tests for `CreateOrderUseCase`.
    - Write Integration Tests for `PostgresOrderRepository`.
    - Write E2E API Tests for `/orders`.

## Questions & Risks

- **Risk**: Distributed transaction failure (Cart cleared but Order fail, or vice versa).
    - *Mitigation*: Use "Order First" approach. Create Order in DB (Pending). Then Clear Cart. If Clear Cart fails, we might have a state where items are still in cart but order exists. Ideally, wrap in a mechanism or just accept slight eventual consistency risk for MVP, or use a distributed transaction pattern (Saga) if strictly required. For now, we assume simple failure handling (rollback DB if Cart clear fails is hard if they are different systems, but we can try).
    - *Refined Approach*:
        1. Begin DB Transaction.
        2. Insert Order & Items.
        3. Commit DB Transaction.
        4. Clear Redis Cart. (If this fails, user has an order AND items in cart. Preferable to "No order, no items").