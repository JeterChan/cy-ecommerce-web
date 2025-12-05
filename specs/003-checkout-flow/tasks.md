# Tasks: 建立訂單流程

**Feature Branch**: `003-checkout-flow`
**Status**: Pending
**Spec**: [spec.md](./spec.md)

## Implementation Strategy
- **Frontend Focus**: Implement the full UI flow using Mock Services/Types to simulate backend interactions.
- **Incremental Delivery**:
    1. **Foundation**: Frontend Types (mirroring Data Model) and Mock Store setup.
    2. **UI Flow**: Build the frontend steps (Summary -> Info -> Payment).
    3. **Mock Integration**: Connect the "Submit" action to a Mock Service.
- **Deferral**: Real Backend API and Database implementation are explicitly deferred to a later phase.

## Phase 1: Setup (Frontend)
**Goal**: Initialize project structure and dependencies.

- [x] T001 Verify frontend dependencies (Pinia, Vue Router) in `frontend/package.json`
- [x] T002 Create Checkout page view file in `frontend/src/views/CheckoutPage.vue`
- [x] T003 Initialize Pinia store for checkout in `frontend/src/stores/useCheckoutStore.ts`

## Phase 2: Foundation (Types & Mocks)
**Goal**: Core data structures (TypeScript interfaces) and Mock Service.

- [x] T004 Define TypeScript interfaces (Order, OrderItem) in `frontend/src/types/order.ts`
- [x] T005 Define TypeScript interfaces (ShippingInfo, PurchaserInfo, PaymentInfo) in `frontend/src/types/orderInfo.ts`
- [x] T006 Implement Mock Order Service (simulate network delay/success) in `frontend/src/services/mockOrderService.ts`

## Phase 3: User Story 1 - View Order Details
**Goal**: Users can see what they are buying before paying.
**Story**: [US1] 檢視訂單明細與啟動結帳

- [x] T007 [US1] Add "Go to Checkout" button in Cart component (e.g., `frontend/src/components/Cart/CartSummary.vue`)
- [x] T008 [US1] Implement Order Summary component in `frontend/src/components/Checkout/OrderSummary.vue`
- [x] T009 [US1] Update `useCheckoutStore` to accept cart items and calculate totals in `frontend/src/stores/useCheckoutStore.ts`
- [x] T010 [US1] Integrate Order Summary into `frontend/src/views/CheckoutPage.vue`

## Phase 4: User Story 2 - Information & Shipping
**Goal**: Collect delivery and purchaser information.
**Story**: [US2] 填寫訂購與運送資訊

- [x] T011 [P] [US2] Create Purchaser Info form component in `frontend/src/components/Checkout/PurchaserForm.vue`
- [x] T012 [P] [US2] Create Shipping Info form component in `frontend/src/components/Checkout/ShippingForm.vue`
- [x] T013 [US2] Implement Shipping Method toggle (Home/7-11) logic in `frontend/src/components/Checkout/ShippingForm.vue`
- [x] T014 [US2] Add "Order Note" (備註) text area to `frontend/src/components/Checkout/ShippingForm.vue` (or separate component)
- [x] T015 [US2] Add form validation logic (required fields, phone format) in forms
- [x] T016 [US2] Integrate forms into `frontend/src/views/CheckoutPage.vue` and bind to Store

## Phase 5: User Story 3 - Payment & Completion
**Goal**: Select payment method and finalize the order (Mock).
**Story**: [US3] 選擇付款方式並完成訂單

- [x] T017 [US3] Create Payment Method selection component in `frontend/src/components/Checkout/PaymentMethod.vue`
- [x] T018 [US3] Integrate `MockOrderService` into `useCheckoutStore` action `submitOrder`
- [x] T019 [US3] Connect "Submit Order" button in `frontend/src/views/CheckoutPage.vue` to Store action
- [x] T020 [US3] Create Order Success page in `frontend/src/views/OrderSuccessPage.vue`
- [x] T021 [US3] Implement cart clearing logic in `frontend/src/stores/useCheckoutStore.ts` (upon mock success)

## Phase 6: Polish & Quality
**Goal**: Ensure robustness and good UX.

- [x] T022 Add loading spinners during (Mock) submission in `frontend/src/views/CheckoutPage.vue`
- [x] T023 Add error toast/alert handling for (Mock) failures in `frontend/src/views/CheckoutPage.vue`
- [x] T024 [P] Frontend: Add unit tests for Checkout Store logic in `frontend/tests/stores/checkout.spec.ts`

## Dependencies

1. **Setup** (Phase 1) must complete before **Foundation** (Phase 2).
2. **Foundation** (Phase 2) must complete before User Stories (Types needed).
3. **US3** (Phase 5) requires **Mock Service** (T006) to be ready.

## Parallel Execution Examples

- **Component Development**: PurchaserForm (T011) and ShippingForm (T012) are independent.
- **Store vs UI**: One dev can build the `useCheckoutStore` and `MockOrderService` while another builds the Vue Components.