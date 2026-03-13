# Research: Order Frontend Pages

## Technology Stack

The project uses a standard Vue 3 ecosystem stack. We will strictly adhere to this stack for the new order pages.

- **Framework**: Vue 3 (Composition API with `<script setup>`)
- **Build Tool**: Vite
- **Language**: TypeScript
- **State Management**: Pinia
- **Routing**: Vue Router
- **Styling**: Tailwind CSS + `shadcn/ui` (via `radix-vue` and `class-variance-authority`)
- **HTTP Client**: Axios
- **Icons**: Lucide Vue

## Architecture Decisions

### 1. Service Layer
Currently, the application relies heavily on mock services (e.g., `mockOrderService.ts`). However, the `011-order-module` implies a backend exists or is being built.
**Decision**: We will create a `OrderService.ts` that defines the interface for order operations.
- It will use `axios` for HTTP requests.
- We will implement a `RealOrderService` that connects to `/api/v1/orders`.
- We can keep a `MockOrderService` for development/testing if the backend is not ready, toggled via environment variables.

### 2. State Management
We will use Pinia to manage order state, specifically for:
- Caching the order list (to avoid refetching on every navigation).
- Caching the current order detail.
- Handling loading and error states for order operations.
- Store name: `useOrderStore`

### 3. Component Structure
We will create the following views and components:
- `views/OrderListView.vue`: Displays the list of orders with pagination.
- `views/OrderDetailView.vue`: Displays full details of a single order.
- `components/order/OrderCard.vue`: A summary card for the list view.
- `components/order/OrderItemList.vue`: Reusable component to list items in an order (used in detail view and potentially checkout confirmation).
- `components/order/OrderStatusBadge.vue`: Visual indicator of order status.

### 4. Routing
New routes will be added to `router/index.ts`:
- `/orders`: Lists all orders (requires auth).
- `/orders/:id`: Details of a specific order (requires auth).

## Data Model Discrepancies
The current `Order` type in `frontend/src/types/order.ts` is missing shipping and payment information which is required by **FR-003**.
**Decision**: We will extend the `Order` interface or create a `OrderDetail` interface that includes:
- `shipping_address`: { name, phone, address, ... }
- `payment_info`: { method, status, ... }
- `shipping_info`: { method, tracking_number, ... }

## API Contract (Assumed)
We assume the backend `011-order-module` provides:
- `GET /api/v1/orders`: List orders (with pagination).
- `GET /api/v1/orders/{id}`: Get order details.
- `POST /api/v1/orders/{id}/cancel`: Cancel an order.

## Alternatives Considered
- **GraphQL**: Not used in the current project (REST/Axios is standard).
- **Vuex**: Deprecated in favor of Pinia.
- **Bootstrap/Other UI Libs**: Project already uses Tailwind/Radix, so we stick to that.
