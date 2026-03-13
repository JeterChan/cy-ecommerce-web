# Tasks: Order Module

**Feature**: Order Module (011-order-module)
**Status**: Pending
**Spec**: [spec.md](./spec.md)

## Phase 1: Setup & Configuration
*Goal: Initialize the project structure and prepare the environment for the Order module.*

- [x] T000 Create Phase 1 development guide and checklist ([dev-guide.md](./dev-guide.md), [checklists/phase1-checklist.md](./checklists/phase1-checklist.md))
- [x] T001 Initialize order module directory structure (domain, application, infrastructure, presentation) in `backend/src/modules/order`
- [x] T002 [P] Create `__init__.py` files for all new directories to ensure they are treated as packages
- [x] T003 Check and verify Alembic configuration in `backend/alembic.ini` (should already exist)

## Phase 2: Foundation (Domain & Infrastructure)
*Goal: Define core entities and database schema. This blocks all user stories.*

- [x] T004 Define `OrderStatus` value object (Enum) in `backend/src/modules/order/domain/value_objects.py` *(提前於 Phase 1 完成)*
- [x] T005 [P] Define `Order` and `OrderItem` domain entities in `backend/src/modules/order/domain/entities.py` *(提前於 Phase 1 完成)*
- [x] T006 Define repository abstract interfaces (`IOrderRepository`, `ICartRepository`) in `backend/src/modules/order/domain/repositories.py` *(提前於 Phase 1 完成)*
- [x] T007 Implement SQLAlchemy models for `orders` and `order_items` in `backend/src/modules/order/infrastructure/models.py`
- [x] T008 Generate Alembic migration script for order tables using `alembic revision --autogenerate`
- [x] T009 Apply database migrations using `alembic upgrade head` *(待執行)*
- [x] T010 Implement `RedisCartRepository` to interact with existing Redis cart data in `backend/src/modules/order/infrastructure/repositories/redis_cart_repository.py`

## Phase 3: User Story 1 - Create Order (Priority P1)
*Goal: Allow users to submit orders, clear cart, and snapshot prices.*
*Independent Test: Create an order via API and verify DB record + Cart cleared.*

- [x] T011 [P] [US1] Create Pydantic DTOs (`CreateOrderRequest`, `OrderResponse`, `OrderItemResponse`) in `backend/src/modules/order/application/dtos/`
- [x] T012 [US1] Implement `PostgresOrderRepository.create` method in `backend/src/modules/order/infrastructure/repositories/postgres_order_repository.py` *(提前於 Phase 2 完成)*
- [x] T013 [US1] Implement `CreateOrderUseCase` (handle transaction, calc total, save order, clear cart) in `backend/src/modules/order/application/use_cases/create_order.py`
- [x] T014 [US1] Create API router and `POST /orders` endpoint in `backend/src/modules/order/presentation/routes.py`
- [x] T015 [US1] Register order router in `backend/src/main.py`
- [ ] T016 [US1] Create integration test for Order Creation flow in `backend/tests/integration/modules/order/test_create_order.py`

## Phase 4: User Story 2 - View Orders (Priority P2)
*Goal: Allow users to view their order history and details.*
*Independent Test: Query orders via API and verify response data.*

- [x] T017 [P] [US2] Add `OrderListResponse` and `OrderDetailResponse` DTOs in `backend/src/modules/order/application/dtos/outputs.py` *(提前於 Phase 3 完成)*
- [x] T018 [US2] Implement `PostgresOrderRepository.get_by_id` and `get_by_user_id` methods in `backend/src/modules/order/infrastructure/repositories/postgres_order_repository.py` *(提前於 Phase 2 完成)*
- [x] T019 [US2] Implement `GetOrderUseCase` and `ListUserOrdersUseCase` in `backend/src/modules/order/application/use_cases/get_order.py` and `backend/src/modules/order/application/use_cases/list_orders.py`
- [x] T020 [US2] Add `GET /orders` and `GET /orders/{order_id}` endpoints to `backend/src/modules/order/presentation/routes.py` *(提前於 Phase 3 完成)*
- [ ] T021 [US2] Create integration test for Order Retrieval in `backend/tests/integration/modules/order/test_get_order.py`

## Phase 5: User Story 3 - Manage Orders (Priority P3)
*Goal: Allow updates to order status (CRUD).*
*Independent Test: Update order status via API and verify change.*

- [x] T022 [P] [US3] Add `UpdateOrderStatusRequest` DTO in `backend/src/modules/order/application/dtos/inputs.py` *(提前於 Phase 3 完成)*
- [x] T023 [US3] Implement `PostgresOrderRepository.update` method in `backend/src/modules/order/infrastructure/repositories/postgres_order_repository.py` *(提前於 Phase 2 完成)*
- [x] T024 [US3] Implement `UpdateOrderStatusUseCase` in `backend/src/modules/order/application/use_cases/update_order.py`
- [x] T025 [US3] Add `PATCH /orders/{order_id}/status` endpoint to `backend/src/modules/order/presentation/routes.py`
- [ ] T026 [US3] Create integration test for Order Status Update in `backend/tests/integration/modules/order/test_update_order.py`

## Phase 6: Polish & Cross-Cutting Concerns
*Goal: Final cleanup and verification.*

- [ ] T027 Run full test suite for Order module to ensure no regressions
- [ ] T028 Perform code cleanup and ensure type hinting compliance (`ruff check .`)
- [ ] T029 Verify API documentation (Swagger UI) renders correctly for new endpoints

## Dependencies

- **US1 (Create Order)** depends on Phase 1 & 2 (Foundation)
- **US2 (View Orders)** depends on US1 (needs data to view)
- **US3 (Manage Orders)** depends on US2 (logic re-use for fetching)

## Parallel Execution Examples

- **Phase 3**: DTO creation (T011) can run parallel to Repository implementation (T012).
- **Phase 4**: Frontend integration (if applicable) can start once T020 is complete.
- **Phase 5**: Update logic (T024) can run parallel to Test creation (T026).

## Implementation Strategy

1.  **MVP Focus**: Complete Phase 1-3 first. This delivers the ability to "Buy" items, which is the most critical business value.
2.  **Incremental Delivery**: Deploy US1 before starting US2/3 if possible, or merge to main branch in squashed commits per story.
3.  **Testing**: Integration tests are prioritized over unit tests for repositories to catch DB/SQL issues early.
