---
description: "Task list template for feature implementation"
---

# Tasks: Product Catalog

**Input**: Design documents from `/specs/001-product-catalog/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/`, `frontend/tests/`
- **Mock Data**: `frontend/src/services/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan
- [x] T002 Initialize Vue.js + Vite + TypeScript project in frontend/
- [x] T003 [P] Install and configure Tailwind CSS in frontend/
- [x] T004 [P] Install and configure shadcn-vue in frontend/
- [x] T005 [P] Configure Vitest for unit testing in frontend/
- [x] T006 [P] Install and setup Vue Router in frontend/src/router/index.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Define Product and Tag interfaces in frontend/src/models/Product.ts
- [x] T008 Implement Mock Data Service foundation in frontend/src/services/productService.ts
- [x] T009 [P] Create base layout component in frontend/src/App.vue
- [x] T010 [P] Create initial Home view component in frontend/src/views/HomeView.vue

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - 瀏覽商品列表與詳情 (Priority: P1) 🎯 MVP

**Goal**: 讓訪客能瀏覽商品列表並點擊查看詳情，達成 MVP 核心價值。

**Independent Test**: 驗證首頁顯示 Mock 商品，點擊可導航至詳情頁並顯示正確資訊。

### Implementation for User Story 1

- [x] T011 [P] [US1] Create ProductCard component in frontend/src/components/product/ProductCard.vue
- [x] T012 [US1] Implement getProducts (list) in frontend/src/services/productService.ts (Mock data)
- [x] T013 [US1] Implement getProductById in frontend/src/services/productService.ts (Mock data)
- [x] T014 [US1] Integrate ProductCard into HomeView to display list in frontend/src/views/HomeView.vue
- [x] T015 [P] [US1] Create ProductDetail view in frontend/src/views/ProductDetailView.vue
- [x] T016 [US1] Configure route for product details in frontend/src/router/index.ts
- [x] T017 [US1] Add error handling for missing product (404) in frontend/src/views/ProductDetailView.vue

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - 商品分頁瀏覽 (Priority: P2)

**Goal**: 提供分頁功能，優化大量商品時的瀏覽體驗。

**Independent Test**: 建立多筆 Mock 資料，驗證分頁控制器出現且能切換頁面。

### Implementation for User Story 2

- [x] T018 [US2] Update getProducts in frontend/src/services/productService.ts to support pagination params
- [x] T019 [P] [US2] Create Pagination component in frontend/src/components/ui/Pagination.vue (or use shadcn)
- [x] T020 [US2] Integrate Pagination into HomeView in frontend/src/views/HomeView.vue
- [x] T021 [US2] Update HomeView to handle page change events and fetch new data

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - 搜尋商品 (Priority: P3)

**Goal**: 提供關鍵字搜尋功能，快速查找商品。

**Independent Test**: 輸入關鍵字，列表只顯示匹配的商品。

### Implementation for User Story 3

- [x] T022 [US3] Update getProducts in frontend/src/services/productService.ts to support search query
- [x] T023 [P] [US3] Create SearchBar component in frontend/src/components/ui/SearchBar.vue
- [x] T024 [US3] Integrate SearchBar into HomeView in frontend/src/views/HomeView.vue
- [x] T025 [US3] Implement debounced search logic in frontend/src/views/HomeView.vue

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - 依照標籤篩選 (Priority: P4)

**Goal**: 提供標籤篩選功能，聚焦瀏覽特定類別。

**Independent Test**: 點擊標籤，列表只顯示該分類商品。

### Implementation for User Story 4

- [x] T026 [US4] Implement getTags in frontend/src/services/productService.ts
- [x] T027 [US4] Update getProducts to support tag filtering in frontend/src/services/productService.ts
- [x] T028 [P] [US4] Create TagFilter component (list of badges) in frontend/src/components/product/TagFilter.vue
- [x] T029 [US4] Integrate TagFilter into HomeView in frontend/src/views/HomeView.vue

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T030 [P] Optimize image loading with lazy loading in ProductCard.vue
- [x] T031 Ensure responsive design on mobile devices (Tailwind classes check)
- [x] T032 Run accessibility checks (Tab navigation, ARIA labels)
- [x] T033 Verify Traditional Chinese text across all components

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 (extends list view)
- **User Story 3 (P3)**: Depends on US1 (extends list view) - Independent of US2
- **User Story 4 (P4)**: Depends on US1 (extends list view) - Independent of US2/US3

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- UI Components (ProductCard, SearchBar, TagFilter) can be built in parallel
- Mock service updates for different features can be implemented in parallel (careful with merge conflicts)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
