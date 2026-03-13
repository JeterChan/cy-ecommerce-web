# Quickstart: Order Frontend Pages

## Prerequisites
- Node.js 18+
- Backend Order Service running (or Mock Service enabled)

## Setup

1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Environment Variables**:
   Ensure your `.env.development` or `.env` has the API base URL:
   ```
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   # Optional: Toggle mock service (if implemented)
   VITE_USE_MOCK_ORDER_SERVICE=true 
   ```

## Running the Feature

1. **Start the Frontend**:
   ```bash
   npm run dev
   ```

2. **Access the Pages**:
   - Login to the application (or ensure you have a valid token).
   - Navigate to `/orders` to view the Order List.
   - Click on an order to view `/orders/:id` (Order Detail).

## Verification

1. **List View**:
   - Verify that you see a list of orders.
   - Check pagination controls.

2. **Detail View**:
   - Verify all order details (items, shipping, payment) are displayed correctly.
   - Check the "Cancel Order" button visibility based on order status (only for PENDING).

3. **Cancel Action**:
   - Click "Cancel Order" on a PENDING order.
   - Confirm the status updates to CANCELLED.
