# Quickstart: Shopping Cart

## Prerequisites
- Feature `001-product-catalog` must be implemented.
- Dependencies: `pinia`

## Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Pinia:
   ```bash
   npm install pinia
   ```

3. Run development server:
   ```bash
   npm run dev
   ```

## Usage Scenarios

### Adding to Cart
1. Go to any product detail page (e.g., `/product/1`).
2. Use the +/- buttons to change quantity.
3. Click "加入購物車".
4. Observe the "加入成功" toast or alert.
5. Observe the cart icon in the navbar updates its count.

### Viewing Cart
1. Click the Cart icon in the navbar.
2. Verify the list of items matches what you added.
3. Verify total price is correct.

### Persistence Test
1. Add items to cart.
2. Refresh the browser.
3. Verify items are still in the cart.
