# Actionable Tasks: Sidebar Category Navigation

**Feature**: `008-product-detail-categories`
**Total Tasks**: 13
**User Stories**: 3

## Phase 1: Setup
*(Project initialization and verification)*

- [x] T001 Verify project environment is ready for frontend changes (check imports, package.json).

## Phase 2: Foundational
*(Blocking prerequisites for all user stories)*

**Goal**: Establish the data structures for Categories and link them to Products (using Mock Data).

- [x] T002 Create Category model interface in `frontend/src/models/Category.ts`.
- [x] T003 Update Product model interface to include optional `categoryId` in `frontend/src/models/Product.ts`.
- [x] T004 Implement `CategoryService` with mock data (hierarchy tree) in `frontend/src/services/categoryService.ts`.
- [x] T005 [P] Create unit tests for `CategoryService` (verify tree fetching and id lookup) in `frontend/tests/services/categoryService.spec.ts`.

## Phase 3: User Story 1 (Navigate Categories)
*(Priority: P1)*

**Goal**: Users can see a category list on the PDP and navigate to category pages.
**Test**: Sidebar is visible on desktop PDP; clicking a link changes URL to filter by that category.

- [x] T006 [US1] Create `CategorySidebar` component with basic list rendering (handle long names with CSS truncation) in `frontend/src/components/layout/CategorySidebar.vue`.
- [x] T007 [US1] Update `CategorySidebar` to link items to the home page with tag query (e.g., `/?tag=CategoryName` maps to existing filter logic) in `frontend/src/components/layout/CategorySidebar.vue`.
- [x] T008 [US1] Create component tests for `CategorySidebar` (verify rendering and link generation) in `frontend/tests/components/CategorySidebar.spec.ts`.
- [x] T009 [US1] Update `ProductDetailView` layout to include the Sidebar (Grid layout) in `frontend/src/views/ProductDetailView.vue`.

## Phase 4: User Story 2 (Visualize Context)
*(Priority: P2)*

**Goal**: The sidebar highlights the category of the currently viewed product.
**Test**: When viewing a "Smartphone" product, the "Smartphone" item in the sidebar is styled as active.

- [x] T010 [US2] Update `mockProducts` in `productService` to include valid `categoryId` mapping to categories in `frontend/src/services/productService.ts`.
- [x] T011 [US2] Update `CategorySidebar` to accept `activeCategoryId` prop and apply active styling (ensure parent category expands if child is active) in `frontend/src/components/layout/CategorySidebar.vue`.
- [x] T012 [US2] Update `ProductDetailView` to compute `activeCategoryId` from the current product and pass it to the sidebar in `frontend/src/views/ProductDetailView.vue`.

## Phase 5: User Story 3 (Responsive)
*(Priority: P3)*

**Goal**: Mobile users see an adapted layout (e.g., stacked or collapsible) instead of a broken sidebar.
**Test**: On < 768px width, the sidebar moves below content or collapses.

- [x] T014 [Fix] Update `productService` to support hierarchical filtering: when filtering by a parent category name, include products from its sub-categories. Ensure product tags match category names.

## Dependencies

1.  **Foundational (T002-T005)** must be done first.
2.  **US1 (T006-T009)** depends on Foundational.
3.  **US2 (T010-T012)** depends on US1 (for the sidebar component) and Foundational (for data models).
4.  **US3 (T013)** depends on US1 (component existence).

## Parallel Execution Examples

- **US2 (Data Update)**: T010 (Update mock data) can be done in parallel with T006 (Sidebar creation).
- **US3 (CSS)**: T013 can be prepared in parallel if the DOM structure is agreed upon, but best done after T009.

## Implementation Strategy

- **MVP (US1)**: Just get the list on the screen and working as links.
- **Enhancement (US2)**: Add the context awareness.
- **Polish (US3)**: Fix mobile layout.