# Phase 0 Research: Shopping Cart

**Feature**: Shopping Cart & Add to Cart
**Date**: 2025-12-03
**Status**: Completed

## Technology Decisions

### 1. State Management
- **Decision**: Pinia
- **Rationale**: The Shopping Cart requires global state accessible from multiple components (Product Detail, Navbar, Cart Page). Pinia is the official Vue 3 state management library, simpler and more type-safe than Vuex.
- **Constitution Check**: Aligns with "High Quality" (type safety) and "Avoid Overdesign" (lightweight compared to Vuex 4).
- **Setup**: `npm install pinia`

### 2. Persistence
- **Decision**: LocalStorage via Pinia Plugin (e.g., `pinia-plugin-persistedstate` or manual watch)
- **Rationale**: Requirement FR-004 mandates persistence. A simple `watch` effect on the cart store to sync with `localStorage` is sufficient for MVP without extra dependencies (MVP First).
- **Implementation**:
  ```typescript
  // Simple manual persistence
  watch(cartState, (state) => {
    localStorage.setItem('cart', JSON.stringify(state))
  }, { deep: true })
  ```

### 3. UI Components
- **Decision**: Extend existing `shadcn-vue` + Tailwind
- **Rationale**: Reusing the stack from `001-product-catalog`. Need new components for:
  - `QuantitySelector`: Custom component using Tailwind.
  - `CartIcon`: Using `lucide-vue-next` (already installed).
  - `CartItem`: New component for the cart list.

## Unknowns & Resolutions

| Unknown | Resolution |
|---------|------------|
| Product Data in Cart | Cart will store `productId` and a snapshot of `price`/`name` to avoid refetching on every cart view (MVP approach). |
| Max Quantity | Hardcode max quantity to 10 or 99 per item for MVP to prevent UI overflow. |

## Action Plan
1. Install and configure Pinia in `frontend/`.
2. Create `useCartStore` with state, actions (add, remove, update), and getters (total items, total price).
3. Implement `QuantitySelector` component.
4. Update `ProductDetailView` to use `QuantitySelector` and call `cartStore.addToCart`.
5. Update `Navbar` (in `App.vue`) to show Cart Icon with badge.
6. Create `CartView` to list items and allow modification.
