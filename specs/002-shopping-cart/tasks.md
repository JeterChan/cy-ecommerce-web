# Tasks: Shopping Cart

**Feature**: Shopping Cart (`002-shopping-cart`)
**Status**: Pending
**Spec**: [specs/002-shopping-cart/spec.md](spec.md)

## Phase 1: Setup
**Goal**: Initialize state management library.

- [x] T001 Install Pinia dependency in `frontend/package.json` (run `npm install pinia`)
- [x] T002 Register Pinia instance in `frontend/src/main.ts`

## Phase 2: Foundational
**Goal**: Create the core data structures and state management logic required for the cart.
**Blocking**: Must be completed before any User Story tasks.

- [x] T003 Create Cart data models (interfaces) in `frontend/src/models/Cart.ts`
- [x] T004 Implement Cart Store with state, actions, getters, and LocalStorage persistence in `frontend/src/stores/cart.ts`

## Phase 3: User Story 1 - Add to Cart (P1)
**Goal**: Enable users to add products to the cart with a specific quantity from the product detail page.
**Story**: [US1] 將商品加入購物車
**Independent Test**: Go to a product page, select quantity > 1, click "Add to Cart". Verify item appears in LocalStorage (key 'cart') with correct data.

- [x] T005 [US1] Create QuantitySelector component in `frontend/src/components/ui/QuantitySelector.vue`
- [x] T006 [US1] Integrate QuantitySelector and "Add to Cart" button with store logic in `frontend/src/views/ProductDetailView.vue`

## Phase 4: User Story 2 - Navbar Entry (P2)
**Goal**: Provide access to the cart from the global navigation.
**Story**: [US2] 透過 Navbar 進入購物車
**Independent Test**: Click Cart icon in Navbar. Verify URL changes to `/cart`. Verify badge number matches total items in store.

- [x] T007 [US2] Add Cart route configuration in `frontend/src/router/index.ts`
- [x] T008 [US2] Implement Navbar Cart Icon with dynamic badge count in `frontend/src/App.vue`

## Phase 5: User Story 3 - View Cart (P3)
**Goal**: Display the cart contents and allow users to review their selection.
**Story**: [US3] 瀏覽購物車內容
**Independent Test**: Add items to cart, navigate to `/cart`. Verify all items are listed with correct subtotal and grand total.

- [x] T009 [P] [US3] Create CartItem component for individual rows in `frontend/src/components/cart/CartItem.vue`
- [x] T010 [P] [US3] Create CartSummary component for totals in `frontend/src/components/cart/CartSummary.vue`
- [x] T011 [US3] Implement CartView page to list items and use summary component in `frontend/src/views/CartView.vue`

## Phase 6: Polish & Cross-Cutting
**Goal**: Ensure UI responsiveness and handle edge cases.

- [x] T012 Verify and refine responsive layout (mobile stack view) in `frontend/src/views/CartView.vue`
- [x] T013 Ensure empty state handling (friendly message + "Go Shopping" link) in `frontend/src/views/CartView.vue`

## Dependencies

1. **Setup & Foundational** (T001-T004) must be done first.
2. **US1** (T005-T006) depends on Foundational.
3. **US2** (T007-T008) depends on Foundational (for store access) and T007 (for route).
4. **US3** (T009-T011) depends on Foundational and T007.

## Implementation Strategy
- **MVP**: Complete Phases 1, 2, and 3 to allow adding items.
- **Incremental**: Add Navbar access (Phase 4) and then the full Cart Page (Phase 5).
- **Parallelism**: T009 (Item) and T010 (Summary) can be built in parallel once Models are defined.
