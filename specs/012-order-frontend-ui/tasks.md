# Tasks: 建立訂單相關的前端頁面 (Create Order Frontend Pages)

**Feature**: `012-order-frontend-ui`
**Status**: Pending
**Spec**: [specs/012-order-frontend-ui/spec.md](../spec.md)

## Implementation Strategy
- **MVP First**: We will first implement the data types and service layer, then build the List View (US1), followed by the Detail View (US2), and finally the Cancel functionality (US3).
- **Component-Driven**: Reusable components (`OrderCard`, `OrderStatusBadge`) will be built in parallel with the views where possible.
- **Mock-First Development**: Since the backend might be in development, we will ensure the `mockOrderService` is robust enough to support UI development.

## Dependencies
- **US1 (View Order List)**: Depends on Phase 1 (Setup).
- **US2 (View Order Details)**: Depends on US1 components (Badge) and Phase 1.
- **US3 (Cancel Order)**: Depends on US2 (UI location).

---

## Phase 1: Setup & Infrastructure
**Goal**: Establish the data structures, service layer, and state management required for order features.

- [x] T001 Define updated `Order`, `OrderDetail`, and related interfaces in `frontend/src/types/order.ts`
- [x] T002 Verify and update `PurchaserInfo`, `ShippingInfo`, `PaymentInfo` in `frontend/src/types/orderInfo.ts`
- [x] T003 [P] Implement `OrderService` with Axios in `frontend/src/services/orderService.ts`
- [x] T004 Update `frontend/src/services/mockOrderService.ts` to return data matching the new `OrderDetail` interface
- [x] T005 [P] Initialize Pinia store `useOrderStore` with state and basic actions in `frontend/src/stores/useOrderStore.ts`

---

## Phase 2: User Story 1 - View Order List (P1)
**Goal**: Allow users to see a paginated list of their historical orders.
**Test**: User can navigate to `/orders`, see a list of orders with correct badges, and use pagination.

- [x] T006 [P] [US1] Create `OrderStatusBadge` component in `frontend/src/components/order/OrderStatusBadge.vue`
- [x] T007 [P] [US1] Create `OrderCard` component using `OrderStatusBadge` in `frontend/src/components/order/OrderCard.vue`
- [x] T008 [US1] Implement `fetchOrders` action in `frontend/src/stores/useOrderStore.ts`
- [x] T009 [US1] Create `OrderListView` page with `OrderCard` and pagination in `frontend/src/views/OrderListView.vue`
- [x] T010 [US1] Register `/orders` route in `frontend/src/router/index.ts`

---

## Phase 3: User Story 2 - View Order Details (P1)
**Goal**: Allow users to click an order and view full details including items, shipping, and payment info.
**Test**: Clicking an order in the list navigates to details; direct URL access works; 404 handled.

- [x] T011 [P] [US2] Create `OrderItemList` component to display line items in `frontend/src/components/order/OrderItemList.vue`
- [x] T012 [US2] Implement `fetchOrderDetails` action in `frontend/src/stores/useOrderStore.ts`
- [x] T013 [US2] Create `OrderDetailView` using `OrderItemList` and displaying full info in `frontend/src/views/OrderDetailView.vue`
- [x] T014 [US2] Register `/orders/:id` route in `frontend/src/router/index.ts`

---

## Phase 4: User Story 3 - Cancel Order (P2)
**Goal**: Allow users to cancel orders that are still in "PENDING" status.
**Test**: "Cancel" button only appears for PENDING orders; clicking it updates status to CANCELLED.

- [x] T015 [US3] Add `cancelOrder` method to `frontend/src/services/orderService.ts` (and mock service)
- [x] T016 [US3] Add `cancelOrder` action to `frontend/src/stores/useOrderStore.ts`
- [x] T017 [US3] Add "Cancel Order" button with confirmation dialog in `frontend/src/views/OrderDetailView.vue`

---

## Phase 5: Polish & Cross-Cutting
**Goal**: Ensure a polished user experience and handle edge cases.

- [x] T018 Verify pagination logic works correctly in `frontend/src/views/OrderListView.vue`
- [x] T019 Ensure loading states (skeletons/spinners) are visible during data fetching in views
- [x] T020 Verify error handling (e.g., network error toasts) in `frontend/src/stores/useOrderStore.ts`

---

## Parallel Execution Examples
- **T006 & T007**: Components can be built while T003/T005 (Service/Store) are being set up.
- **T011**: The ItemList component is independent of the main view logic and can be built anytime.