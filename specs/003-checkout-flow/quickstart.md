# Quickstart: 建立訂單流程

**Feature**: 003-checkout-flow
**Environment**: Local Development

## Prerequisites

- Frontend: Node.js 18+, npm/pnpm
- Backend: Python 3.10+, Docker (optional)

## Setup

1. **Backend**:
   ```bash
   # Ensure you are in the backend directory (or root if using docker)
   # If using Docker:
   docker-compose up -d api
   
   # If local:
   # pip install -r requirements.txt
   # python main.py
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Running the Feature

1. Open `http://localhost:5173` (default Vite port).
2. Add items to the cart.
3. Click "前往結帳" (Checkout) in the Cart view.
4. Fill in the form:
   - **Purchaser**: Name, Phone, Email
   - **Shipping**: Name, Phone, Select Method (Home/7-11)
   - **Payment**: Select Method (Credit Card/COD/ATM)
5. Submit the order.
6. Verify you see the Order Confirmation page.

## Testing

### Manual Testing
- Use the **Mock Payment** option to simulate successful payment without real credentials.
- Try selecting "7-11 Store Pickup" and verify store selection logic (or input).

### Automated Tests
- Run frontend unit tests: `npm run test:unit`
