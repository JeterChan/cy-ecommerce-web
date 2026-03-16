# Tasks: Member Cart Async Sync (Celery Implementation)

**Input**: Design documents from `/specs/019-member-cart-async-sync/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths included in descriptions

---

## Phase 1: Setup & Foundational

**Purpose**: Core infrastructure setup for Celery and Hybrid Repository.

- [x] T001 [P] Define `cart_sync_queue` and task routing in `backend/src/infrastructure/celery_app.py`
- [x] T002 Implement `HybridCartRepository` as an orchestrator for Redis and SQL repositories in `backend/src/modules/cart/infrastructure/repositories/hybrid_repository.py`
- [x] T003 [P] Add Redis locking utility for Celery tasks in `backend/src/infrastructure/redis.py`

---

## Phase 3: User Story 1 - 快速加入購物車 (Priority: P1) 🎯 MVP

**Goal**: Immediate response after updating Redis, with Celery task dispatch.

**Independent Test**: API call returns < 30ms and Redis Hash contains updated data.

### Implementation for User Story 1

- [x] T004 [US1] Update `AddToCartUseCase` to use `HybridCartRepository` and trigger Celery task in `backend/src/modules/cart/application/use_cases/cart_commands.py`
- [x] T005 [US1] Update `UpdateCartItemQuantityUseCase` to trigger Celery task in `backend/src/modules/cart/application/use_cases/cart_commands.py`
- [x] T006 [US1] Update `RemoveFromCartUseCase` to trigger Celery task in `backend/src/modules/cart/application/use_cases/cart_commands.py`
- [x] T007 [US1] Update `get_cart_repository` dependency to return `HybridCartRepository` for members in `backend/src/modules/cart/presentation/routes.py`
- [x] T015 [US1] Implement Read Fallback in `HybridCartRepository.get_cart` (Read Redis -> If empty, Read DB & Backfill Redis) in `backend/src/modules/cart/infrastructure/repositories/hybrid_repository.py`

**Checkpoint**: User Story 1 functional - Member cart updates are now lightning fast in Redis with fallback support.

---

## Phase 4: User Story 2 - 數據最終一致性同步 (Priority: P1)

**Goal**: Background task reliably persists Redis state to PostgreSQL.

**Independent Test**: After API success, verify PostgreSQL `cart_items` reflects Redis data after worker run.

### Implementation for User Story 2

- [x] T008 [US2] Implement `sync_member_cart_task` with DB transaction and error handling in `backend/src/modules/cart/infrastructure/tasks.py`
- [x] T009 [US2] Implement state-based UPSERT sync logic (Read Redis -> INSERT ... ON CONFLICT -> Clean stale DB items) in `backend/src/modules/cart/infrastructure/tasks.py`
- [x] T010 [US2] Add Celery retry policy and exponential backoff configuration in `backend/src/modules/cart/infrastructure/tasks.py`
- [x] T011 [US2] Add integration test for end-to-end sync (API -> Redis -> Worker -> PostgreSQL) in `backend/tests/integration/test_cart_sync_task.py`

**Checkpoint**: User Story 2 functional - Data is safely and non-blockingly persisted to PostgreSQL.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Handling edge cases and performance verification.

- [x] T012 [P] Implement Redis lock in `sync_member_cart_task` to prevent concurrent syncs for the same user in `backend/src/modules/cart/infrastructure/tasks.py`
- [x] T013 Update `specs/019-member-cart-async-sync/README.md` with final implementation details and worker monitoring instructions
- [x] T014 Run performance benchmark to verify SC-001 (API < 30ms) and SC-002 (Sync < 2s)

---

## Dependencies & Execution Order

### Phase Dependencies

1. **Phase 1** -> **Phase 3** (Foundations required for Use Case updates)
2. **Phase 3** -> **Phase 4** (API must trigger tasks before Worker can be tested)
3. **Phase 4** -> **Phase 5** (Integration must be stable before benchmarks)

### Parallel Opportunities

- T001, T003 can run in parallel with repository design.
- T004, T005, T006 can be updated in parallel within the same file.
- T013, T014 can be done in parallel at the end.

---

## Implementation Strategy

### MVP First (User Story 1 & 2 Together)

For this specific feature, US1 and US2 are tightly coupled. We recommend:
1. Setup basic Celery task structure.
2. Update API to write to Redis and dispatch task.
3. Implement basic Worker to write to PostgreSQL using UPSERT.
4. Verify end-to-end flow.

### Incremental Delivery

1. Setup Infrastructure (Phase 1)
2. Fast API Writes with Fallback (Phase 3)
3. Robust Sync Worker (Phase 4)
4. Failure Handling & Performance (Phase 5)
