# Tasks: Cart Redis Optimization & Stock Validation (DDD Alignment)

**Input**: Design documents from `/specs/018-cart-redis-optimization/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths included in descriptions

---

## Phase 1: Setup & Foundational (Prerequisites)

**Purpose**: Update existing interfaces and infrastructure to support cross-module logic.

- [x] T001 Add `get_by_id_with_lock` to `IProductRepository` in `backend/src/modules/product/domain/repository.py`
- [x] T002 Implement `get_by_id_with_lock` with `FOR SHARE` in `SqlAlchemyProductRepository` in `backend/src/modules/product/infrastructure/repository.py`
- [x] T003 Ensure `redis` is properly configured for the current environment in `backend/src/infrastructure/config.py`

---

## Phase 2: User Story 1 - Add to Cart with Stock Check (Priority: P1) 🎯 MVP

**Goal**: Implement real-time stock validation using database locks before adding items to Redis.

**Independent Test**: Use `POST /api/v1/cart/items` with a quantity exceeding database stock and verify `400 Bad Request`.

### Implementation for User Story 1

- [x] T004 [US1] Update `AddToCartUseCase` to accept `IProductRepository` and `AsyncSession` in `backend/src/modules/cart/application/use_cases/cart_commands.py`
- [x] T005 [US1] Implement `FOR SHARE` stock check logic within `AddToCartUseCase.execute` in `backend/src/modules/cart/application/use_cases/cart_commands.py`
- [x] T006 [US1] Update `get_cart_repository` or `add_to_cart` route to inject `ProductRepository` and `AsyncSession` in `backend/src/modules/cart/presentation/routes.py`
- [x] T007 [US1] Add integration test for concurrent stock validation in `backend/tests/integration/test_cart_redis_optimization.py`

**Checkpoint**: User Story 1 is functional - adding items to cart is now guarded by real-time stock locks.

---

## Phase 3: User Story 2 - View Cart with Dynamic Pricing (Priority: P1)

**Goal**: Ensure the existing view logic remains consistent with dynamic pricing requirements.

**Independent Test**: Update a product price in the DB and refresh the cart to see the new price.

### Implementation for User Story 2

- [x] T008 [US2] Verify and ensure `enrich_cart_items_with_product_info` correctly fetches current prices in `backend/src/modules/cart/presentation/routes.py`
- [x] T009 [US2] Add integration test for dynamic price calculation in `backend/tests/integration/test_cart_redis_optimization.py`

**Checkpoint**: User Story 2 is verified - cart view displays live database prices.

---

## Phase 4: Polish & Performance

**Purpose**: Final validation and clean-up.

- [x] T010 [P] Implement centralized error handling for stock-related exceptions in `backend/src/modules/cart/presentation/routes.py` or dedicated error handler.
- [x] T011 [P] Validate SC-001 (Redis retrieval < 50ms) and SC-004 (Validation < 200ms) performance metrics.
- [x] T012 Update `specs/018-cart-redis-optimization/README.md` with final implementation summary.

---

## Dependencies & Execution Order

### Phase Dependencies

1. **Phase 1** -> **Phase 2** (Required for the `ProductRepository` changes)
2. **Phase 2** -> **Phase 3** (Sequential implementation of stories)
3. **Phase 3** -> **Phase 4** (Final polish)

### Parallel Opportunities

- T001 and T002 must be sequential, but can be done while reviewing US2 logic (T008).
- T010 and T011 can be done in parallel once logic is implemented.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

The primary goal is the secure stock-checked add operation.

1. Enhance `ProductRepository` with locking.
2. Inject it into `AddToCartUseCase`.
3. Validate with tests.

### Incremental Delivery

1. Setup Repository Locking -> Foundation ready.
2. Implement US1 -> Secure storage and validation ready.
3. Verify US2 -> Dynamic pricing confirmed.
4. Polish -> Ready for production.
