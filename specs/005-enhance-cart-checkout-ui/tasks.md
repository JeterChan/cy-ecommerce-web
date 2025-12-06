# Tasks: Enhance Cart and Checkout UI Layout

**Branch**: `005-enhance-cart-checkout-ui` | **Date**: 2025-12-06 | **Spec**: [specs/005-enhance-cart-checkout-ui/spec.md](spec.md)
**Context**: Improve UI consistency by integrating Navbar/Footer and adding navigation controls to Cart and Checkout pages.

## Implementation Strategy

- **MVP First**: Focus on extracting the Footer and integrating it into Cart and Checkout views immediately.
- **Incremental Delivery**:
    1.  Refactor HomeView to extract Footer.
    2.  Update CartView with Navbar, Footer, and "Continue Shopping".
    3.  Update CheckoutPage with Navbar, Footer, and "Back to Cart".
- **Testing**: Verify visually and via navigation links manually (Quickstart) and ensure unit tests pass.

## Dependencies

- **US1 (Cart Navigation)** depends on **Phase 2 (Footer Extraction)**
- **US2 (Checkout Navigation)** depends on **Phase 2 (Footer Extraction)**

---

## Phase 1: Setup

- [x] T001 Verify project dependencies (Vue Router, lucide-vue-next, shadcn-vue) in `frontend/package.json`

## Phase 2: Foundational (Blocking Prerequisites)

- [x] T002 [P] Create `Footer` component in `frontend/src/components/layout/Footer.vue` by extracting content from `HomeView`
- [x] T003 [P] Update `frontend/src/views/HomeView.vue` to use the new `Footer` component
- [x] T004 Verify Home page still renders footer correctly via `npm run dev`

## Phase 3: User Story 1 (View Shopping Cart with Navigation)

*Goal: Shopper sees global navigation and can return to shopping from the cart.*

- [x] T005 [US1] Update `frontend/src/views/CartView.vue` layout to include `Navbar` and `Footer` (flex-col, min-h-screen)
- [x] T006 [US1] Add "Continue Shopping" button to `frontend/src/views/CartView.vue` using shadcn Button and router push to `/`
- [x] T007 [US1] Verify Cart page layout and navigation link via `npm run dev`

## Phase 4: User Story 2 (Checkout with Navigation Context)

*Goal: Shopper sees global navigation and can return to cart from checkout.*

- [x] T008 [US2] Update `frontend/src/views/CheckoutPage.vue` layout to include `Navbar` and `Footer` (flex-col, min-h-screen)
- [x] T009 [US2] Add "Back to Cart" button to `frontend/src/views/CheckoutPage.vue` using shadcn Button and router push to `/cart`
- [x] T010 [US2] Verify Checkout page layout and navigation link via `npm run dev`

## Phase 5: Polish & Cross-Cutting Concerns

- [x] T011 Verify responsiveness of new layouts on mobile viewport
- [x] T012 Run full test suite `npm run test:unit` to ensure no regressions
- [x] T013 Update `specs/005-enhance-cart-checkout-ui/quickstart.md` if any steps changed (optional)
