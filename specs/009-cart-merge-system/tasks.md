# Tasks: Backend Cart Merge System

**Feature**: Backend Cart Merge System
**Branch**: `009-cart-merge-system`
**Status**: Phase 5 Completed, Core Features Done, Ready for Migration

## Phase 1: Setup ✅ COMPLETED

- [x] T001 [P] Install Redis dependencies in backend/requirements.txt
- [x] T002 Configure Redis connection settings in backend/src/infrastructure/config.py
- [x] T003 Implement Redis client wrapper in backend/src/infrastructure/database.py

## Phase 2: Foundation (Blocking) ✅ COMPLETED

- [x] T004 Create CartItem Pydantic schemas in backend/src/modules/cart/domain/schemas.py
- [x] T005 Create CartItem SQLAlchemy model in backend/src/modules/cart/infrastructure/models.py
- [x] T006 Implement Guest Token utility (Cookie generation) in backend/src/modules/cart/domain/utils.py
- [x] T007 [P] Create abstract CartRepository interface in backend/src/modules/cart/domain/repository.py

## Phase 3: User Story 1 - Guest Cart (Priority: P1) ✅ COMPLETED

**Goal**: Enable guests to manage cart items without login.
**Independent Test**: Use API to add/view items with just a cookie.

- [x] T008 [US1] Implement RedisCartRepository for guest operations in backend/src/modules/cart/infrastructure/redis_repository.py
- [x] T009 [US1] Create Cart Use Cases (Commands & Queries) in backend/src/modules/cart/application/use_cases/
- [x] T010 [US1] Implement Guest Cart API endpoints in backend/src/modules/cart/presentation/routes.py
- [x] T011 [US1] Register cart router in backend/src/main.py
- [ ] T012 [P] [US1] Create integration tests for Guest Cart in backend/tests/modules/cart/test_guest_cart.py

**Phase 3 Notes**:
- ✅ RedisCartRepository 完整實作（支援 CRUD、批量操作）
- ✅ Use Cases 符合 Clean Architecture（Commands & Queries 分離）
- ✅ API Endpoints 完整（7 個 endpoints）
- ✅ 購物車不儲存價格（動態查詢 Product）
- ⏳ 整合測試待補（可在 Phase 6 完成）

## Phase 4: User Story 2 - Member Cart (Priority: P1) ✅ COMPLETED

**Goal**: Enable members to manage persistent cart.
**Independent Test**: Use API with Bearer token; verify DB persistence.

- [x] T013 [US2] Implement SQLCartRepository for member persistence in backend/src/modules/cart/infrastructure/sql_repository.py
- [x] T015 [US2] Update API endpoints to detect User from Token in backend/src/modules/cart/presentation/routes.py
- [ ] T016 [P] [US2] Create integration tests for Member Cart in backend/tests/modules/cart/test_member_cart.py

**Phase 4 Notes**:
- ✅ SQLCartRepository 完整實作（與 RedisCartRepository 共用介面）
- ✅ API 自動識別會員/訪客（透過 JWT Token 或 Cookie）
- ✅ 會員購物車持久化到 PostgreSQL
- ✅ 訪客購物車維持 Redis 儲存
- ⚠️ 需要執行 Database Migration 建立 carts 和 cart_items 表
- ⏳ 整合測試待補（可在 Phase 6 完成）

## Phase 5: User Story 3 - Merge Cart (Priority: P1) ✅ COMPLETED

**Goal**: Merge guest items into member cart upon login.
**Independent Test**: Simulate login flow and verify item transfer.

- [x] T017 [US3] Implement Merge Logic (Redis Guest -> SQL Member) in backend/src/modules/cart/application/services/merge_service.py
- [x] T018 [US3] Integrate Merge Service into Auth Login flow in backend/src/modules/auth/presentation/routes.py
- [ ] T019 [P] [US3] Create unit tests for Merge Logic in backend/tests/modules/cart/test_merge_logic.py
- [ ] T020 [P] [US3] Create integration tests for Login Merge in backend/tests/modules/cart/test_merge_integration.py

**Phase 5 Notes**:
- ✅ CartMergeService 完整實作（支援數量累加、錯誤隔離）
- ✅ 整合到 Auth Login 流程（自動執行）
- ✅ 購物車合併失敗不影響登入（錯誤邊界）
- ✅ 支援 get_merge_preview（預覽合併結果）
- ✅ 使用 batch_add_items 批量合併（效能優化）
- ⏳ 單元測試與整合測試待補（可在 Phase 6 完成）

## Phase 6: Polish & Cross-Cutting

- [ ] T021 [P] Add OpenAPI documentation for Cart endpoints in backend/src/modules/cart/api/routes.py
- [ ] T022 Implement error handling for invalid products or quantities in backend/src/modules/cart/domain/service.py
- [ ] T023 Run final linting and type checking (ruff, mypy)

## Dependencies

- Phase 1 & 2 must complete before Phase 3.
- Phase 3 (Guest) & Phase 4 (Member) can be developed in parallel, but Service layer needs careful design to support both strategies.
- Phase 5 (Merge) depends on both Phase 3 and Phase 4.

## Implementation Strategy

1. **MVP Scope**: Focus on Guest Cart (Phase 3) first to validate Redis interaction.
2. **Incremental Delivery**: Add Member persistence (Phase 4) next.
3. **Integration**: Finally wire up the Merge logic (Phase 5).
