---
description: "Task list for Store Homepage & Navigation feature"
---

# Tasks: Store Homepage & Navigation

**Input**: Design documents from `/specs/004-store-homepage/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/homepage-api.yaml

**Tests**: Included as TDD tasks since the plan emphasizes "Verify (Tests)".
**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- `frontend/src/` for all source code
- `frontend/src/components/` for Vue components
- `frontend/src/views/` for page views
- `frontend/src/services/` for data services

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Verify project dependencies in frontend/package.json
- [x] T002 [P] Create directory structure for homepage components in frontend/src/components/home/
- [x] T003 [P] Create directory structure for layout components in frontend/src/components/layout/
- [x] T024 Install Carousel dependencies (embla-carousel-vue) and add UI components in frontend/src/components/ui/carousel/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Update Product model with `is_featured` field in frontend/src/models/Product.ts
- [x] T005 Create Promotion model interface in frontend/src/models/Promotion.ts
- [x] T006 [P] Create mock Promotion service in frontend/src/services/promotionService.ts
- [x] T007 Update Product service mock to handle `is_featured` filtering in frontend/src/services/productService.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Seasonal Featured Products (Priority: P1) 🎯 MVP

**Goal**: Display featured products section on the homepage

**Independent Test**: Load root URL, verify "Seasonal Featured Products" section displays cards with image, name, and price.

### Tests for User Story 1 (Component Tests)

- [x] T008 [P] [US1] Create test for FeaturedProducts component in frontend/src/components/home/__tests__/FeaturedProducts.spec.ts

### Implementation for User Story 1

- [x] T009 [P] [US1] Create ProductCard component (if not existing) or verify reuse in frontend/src/components/product/ProductCard.vue
- [x] T025 [US1] Refactor FeaturedProducts to use Carousel instead of Grid in frontend/src/components/home/FeaturedProducts.vue
- [x] T026 [US1] Add "View All" link to FeaturedProducts component in frontend/src/components/home/FeaturedProducts.vue
- [x] T010 [US1] Implement FeaturedProducts component using ProductService in frontend/src/components/home/FeaturedProducts.vue (Superseded by T025)
- [x] T011 [US1] Create HomeView view and add FeaturedProducts section in frontend/src/views/HomeView.vue
- [x] T012 [US1] Configure root route to point to HomeView in frontend/src/router/index.ts

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Navigate Categories via Dropdown (Priority: P1)

**Goal**: Enable navigation to category pages via Navbar dropdown

**Independent Test**: Interact with Navbar, verify dropdown opens, click category, verify navigation.

### Tests for User Story 2 (Component Tests)

- [x] T013 [P] [US2] Create test for Navbar dropdown behavior in frontend/src/components/layout/__tests__/Navbar.spec.ts

### Implementation for User Story 2

- [x] T014 [P] [US2] Implement Navbar component with "Categories" link in frontend/src/components/layout/Navbar.vue
- [x] T015 [US2] Implement Dropdown menu logic fetching tags from ProductService in frontend/src/components/layout/Navbar.vue
- [x] T016 [US2] Integrate Navbar into App.vue or Main Layout in frontend/src/App.vue
- [x] T017 [US2] Ensure routing for category filtering works (reuse/verify ProductList view) in frontend/src/views/HomeView.vue

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - View Discount Promotion Info (Priority: P2)

**Goal**: Display promotional discount text on the homepage

**Independent Test**: Inspect homepage for promotional text block.

### Tests for User Story 3 (Component Tests)

- [x] T018 [P] [US3] Create test for PromotionBlock rendering in frontend/src/components/home/__tests__/PromotionBlock.spec.ts

### Implementation for User Story 3

- [x] T019 [US3] Implement PromotionBlock component fetching data from PromotionService in frontend/src/components/home/PromotionBlock.vue
- [x] T020 [US3] Add PromotionBlock to HomeView layout in frontend/src/views/HomeView.vue

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T021 [P] Add loading states for async data fetching in HomeView.vue
- [x] T022 Verify responsive behavior (mobile view) for Navbar and Grid
- [x] T023 Update documentation in README.md with new feature info

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Blocks User Stories.
- **User Stories (Phase 3+)**: Depend on Foundational.

### User Story Dependencies

- **User Story 1 (P1)**: Independent after Foundational.
- **User Story 2 (P1)**: Independent after Foundational.
- **User Story 3 (P2)**: Independent after Foundational.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & 2.
2. Complete Phase 3 (User Story 1).
3. **STOP and VALIDATE**: Ensure homepage loads with products.

### Incremental Delivery

1. Add User Story 2 (Navigation).
2. Add User Story 3 (Promotion).
3. Polish responsive design.