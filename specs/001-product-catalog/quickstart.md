# Quickstart: Product Catalog Frontend

## Prerequisites
- Node.js 18+
- npm or yarn

## Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run development server:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:5173`.

## Running Tests

- Unit Tests (Vitest):
  ```bash
  npm run test:unit
  ```

## Project Structure

- `src/components/ui`: Reusable UI components (shadcn-vue)
- `src/views`: Page components (Home, ProductDetail)
- `src/services`: API integration (or mock services)
- `src/types`: TypeScript definitions

## Mocking
Currently, the frontend uses a mock service (`src/services/productService.ts`) to simulate API calls. No backend is required to run the frontend.
