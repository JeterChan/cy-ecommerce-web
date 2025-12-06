# Quickstart: Enhance Cart and Checkout UI Layout

## Prerequisites
-   Node.js 18+
-   `npm` or `pnpm` installed

## Setup
1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies (if not already installed):
    ```bash
    npm install
    ```

## Running the Application
1.  Start the development server:
    ```bash
    npm run dev
    ```
2.  Open your browser to the URL shown (usually `http://localhost:5173`).

## Verifying the Changes

### Shopping Cart
1.  Add an item to your cart from the Home page.
2.  Click the Cart icon in the Navbar to go to `/cart`.
3.  **Check**:
    -   Navbar is visible at the top.
    -   Footer is visible at the bottom.
    -   A "Continue Shopping" (繼續購物) button is visible.
4.  Click "Continue Shopping" and verify it takes you back to Home.

### Checkout
1.  From the Cart page, click "Checkout" (or equivalent proceed button).
2.  **Check**:
    -   Navbar is visible at the top.
    -   Footer is visible at the bottom.
    -   A "Back to Cart" (返回購物車) button is visible.
3.  Click "Back to Cart" and verify it takes you back to the Cart page.

## Testing
Run the frontend test suite to ensure no regressions:
```bash
npm run test:unit
```
