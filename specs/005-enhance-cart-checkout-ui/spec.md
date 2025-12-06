# Specification: Enhance Cart and Checkout UI Layout

## 1. Introduction

This feature focuses on improving the consistency of the user interface across the shopping journey. It involves updating the Shopping Cart and Checkout pages to include the global navigation elements (Navbar and Footer) and adding specific navigation controls to improve user flow between these steps and the main store.

## 2. User Scenarios

### 2.1. View Shopping Cart with Navigation
**Actor**: Shopper
**Preconditions**: None (can view empty cart)
**Flow**:
1. Shopper navigates to the Shopping Cart page.
2. System displays the global Navbar at the top.
3. System displays the Cart contents.
4. System displays a "Continue Shopping" link or button.
5. System displays the global Footer at the bottom.
6. Shopper clicks "Continue Shopping".
7. System redirects Shopper to the Home page (product listing).

### 2.2. Checkout with Navigation Context
**Actor**: Shopper
**Preconditions**: Cart is not empty.
**Flow**:
1. Shopper proceeds to Checkout from the Cart page.
2. System displays the global Navbar at the top.
3. System displays the Checkout form.
4. System displays a "Back" (or "Return to Cart") link or button.
5. System displays the global Footer at the bottom.
6. Shopper clicks the "Back" link.
7. System redirects Shopper back to the Shopping Cart page.

## 3. Functional Requirements

### 3.1. Global Layout Components
1.  **Reusable Footer**: The existing footer section (currently in Home page) MUST be extracted into a reusable component (e.g., `Footer.vue`) to ensure consistent content (copyright, links) across all pages.
2.  **Navbar Integration**: The existing `Navbar` component MUST be included on both the Cart and Checkout pages.

### 3.2. Shopping Cart Page Updates
1.  **Layout**: The page MUST use a layout that includes the Navbar (top) and Footer (bottom), with the cart content centered in between.
2.  **Continue Shopping**: A clearly visible link or button labeled "Continue Shopping" (or similar localized text like "繼續購物") MUST be added.
    -   **Action**: Clicking this element redirects the user to the Home page (`/`).

### 3.3. Checkout Page Updates
1.  **Layout**: The page MUST use a layout that includes the Navbar (top) and Footer (bottom).
2.  **Back Navigation**: A clearly visible link or button labeled "Back to Cart" (or similar localized text like "返回購物車" or "返回上一步") MUST be added.
    -   **Action**: Clicking this element redirects the user to the Shopping Cart page (`/cart`).
    -   **Placement**: Should be placed logically, typically near the top of the form or next to the primary "Submit Order" action for easy access.

## 4. Non-Functional Requirements

1.  **Consistency**: The Navbar and Footer on the Cart and Checkout pages MUST visually match the Home page in terms of styling, spacing, and behavior.
2.  **Responsiveness**: The new layout elements and navigation links MUST be responsive and usable on mobile devices.

## 5. Success Criteria

1.  **Visual Verification**:
    -   The Cart page renders with the Navbar at the top and Footer at the bottom.
    -   The Checkout page renders with the Navbar at the top and Footer at the bottom.
2.  **Navigation Verification**:
    -   Clicking "Continue Shopping" on the Cart page successfully navigates to the Home page.
    -   Clicking "Back to Cart" on the Checkout page successfully navigates to the Cart page.
3.  **Component Reusability**:
    -   The Footer is implemented as a shared component, not duplicated code.

## 6. Assumptions

1.  The "Home" page serves as the main product catalog/browsing area.
2.  The existing `Navbar` component is self-contained and handles its own state (e.g., cart count) correctly when mounted on different views.