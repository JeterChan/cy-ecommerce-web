# Data Model: Enhance Cart and Checkout UI Layout

## Overview
This feature is primarily UI/Layout focused and does not introduce new persistent entities or database schema changes. The data model changes are limited to component props and potential local state for UI control.

## Entities

### Layout Components (Frontend)

**Footer.vue**
-   **Type**: UI Component
-   **Props**: None (Static content initially)
-   **Events**: None
-   **Dependencies**: `lucide-vue-next` (for social icons if any)

**CartView.vue (Updates)**
-   **State**: Inherits existing Cart Store state.
-   **New UI Elements**:
    -   `Navbar` (Component)
    -   `Footer` (Component)
    -   "Continue Shopping" Button (Router Navigation)

**CheckoutPage.vue (Updates)**
-   **State**: Inherits existing Checkout/Cart state.
-   **New UI Elements**:
    -   `Navbar` (Component)
    -   `Footer` (Component)
    -   "Back to Cart" Button (Router Navigation)

## Persistence
-   **LocalStorage**: Existing Cart persistence remains unchanged.
-   **Backend**: No changes.

## Validation Rules
-   N/A (UI only)
