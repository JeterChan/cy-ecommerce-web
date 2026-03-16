# Tasks: Order Checkout and Management System

**Feature Name**: Order Checkout and Management System
**Branch**: `020-order-checkout-system`
**Spec**: [specs/020-order-checkout-system/spec.md]
**Implementation Plan**: [specs/020-order-checkout-system/plan.md]

## Implementation Strategy

We follow an **MVP-first** and **Domain-Driven Design (DDD)** approach.
1. **Setup & Foundation**: Initialize the order module structure and database models.
2. **User Story 1 (P1)**: Implement the core transactional checkout logic. This is the most complex part and requires rigorous atomic failure testing.
3. **User Story 2 (P2)**: Implement order history and detail retrieval.
4. **Validation**: Ensure high concurrency protection works as intended.

## Phase 1: Setup

- [x] T001 Create order module directory structure in `backend/src/modules/order/`
- [x] T002 Initialize `backend/src/modules/order/__init__.py` and sub-packages

## Phase 2: Foundational (Models & Migrations)

- [x] T003 [P] Define `Order` and `OrderItem` SQLAlchemy models in `backend/src/modules/order/infrastructure/models.py`
- [x] T004 [P] Define order-related Pydantic schemas (CheckoutRequest, OrderResponse) in `backend/src/modules/order/application/dtos/`
- [x] T005 Create and run Alembic migration to create `orders` and `order_items` tables

## Phase 3: User Story 1 - Transactional Checkout (Priority: P1)

**Goal**: Implement atomic checkout: Validate stock/price -> Deduct stock (Pessimistic Lock) -> Create Order -> Create Items -> Clear Redis Cart.

**Independent Test**: Use `POST /api/v1/orders/checkout` with items in Redis. Verify DB atomicity by simulating a failure mid-transaction and confirming no partial data exists.

- [x] T006 [US1] Implement `OrderRepository` for basic CRUD in `backend/src/modules/order/infrastructure/repository.py`
- [x] T007 [P] [US1] Create `InsufficientStockException` and `PriceChangedException` in `backend/src/modules/order/domain/exceptions.py`
- [x] T008 [US1] Implement `CheckoutUseCase` with `SELECT ... FOR UPDATE` locking and transaction management in `backend/src/modules/order/application/use_cases/checkout.py`
- [x] T009 [US1] Add Redis cart clearing logic post-DB-commit in `backend/src/modules/order/application/use_cases/checkout.py`
- [x] T010 [US1] Implement checkout endpoint in `backend/src/modules/order/presentation/routes.py`
- [x] T011 [US1] Add integration test for successful atomic checkout in `backend/tests/modules/order/test_checkout_atomic.py`
- [x] T012 [US1] Add integration test for atomic rollback on failure in `backend/tests/modules/order/test_checkout_rollback.py`
- [x] T013 [US1] Add stress test for concurrent stock deduction (pessimistic lock validation) in `backend/tests/modules/order/test_checkout_concurrency.py`

## Phase 4: User Story 2 - Order History & Details (Priority: P2)

**Goal**: Allow users to list their orders and see specific details.

**Independent Test**: Navigate to "My Orders" and click a specific order to see recipient, payment, and items.

- [x] T014 [US2] Implement `GetOrderHistoryUseCase` in `backend/src/modules/order/application/use_cases/get_orders.py`
- [x] T015 [US2] Implement `GetOrderDetailUseCase` in `backend/src/modules/order/application/use_cases/get_order_detail.py`
- [x] T016 [US2] Add list orders endpoint in `backend/src/modules/order/presentation/routes.py`
- [x] T017 [US2] Add order detail endpoint in `backend/src/modules/order/presentation/routes.py`
- [x] T018 [US2] Add integration test for order history and details in `backend/tests/modules/order/test_order_retrieval.py`

## Phase 5: Polish & Cross-cutting Concerns

- [x] T019 Update main API router to include order routes in `backend/src/main.py`
- [x] T020 [P] Implement centralized error handling for order exceptions in `backend/src/core/exceptions.py`
- [x] T021 Perform final audit of database locks and performance

## Dependencies

- **US1** depends on **Phase 2** (Models & Migrations).
- **US2** depends on **Phase 2** and ideally some data created by **US1**.

## Parallel Execution Examples

- **Models & Schemas**: T003 and T004 can be done simultaneously.
- **Exceptions & Infrastructure**: T007 can be done while T006 is being developed.
- **Polish**: T020 can be done anytime after Phase 2.
