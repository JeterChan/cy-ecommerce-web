# Research: Enhance Cart and Checkout UI Layout

## Decisions

### 1. Footer Component Extraction
- **Decision**: Extract the hardcoded footer from `HomeView.vue` into a new component `frontend/src/components/layout/Footer.vue`.
- **Rationale**: Promotes code reuse and consistency across Home, Cart, and Checkout pages (DRY principle). Adheres to the "High Quality" constitution principle.
- **Alternatives considered**:
    -   *Duplicating HTML in each view*: Rejected due to high maintenance cost and violation of DRY.
    -   *Global App Layout (App.vue)*: Rejected for now to minimize refactoring scope (MVP First), as current views manage their own layout structure (e.g. `HomeView` imports `Navbar`). Moving to a global layout wrapper is a larger architectural change better suited for a dedicated refactoring task if needed later.

### 2. Navigation UI Elements
- **Decision**: Use `shadcn-vue` Button components (variant="link" or "ghost") with `lucide-vue-next` icons (e.g., `ArrowLeft`) for "Continue Shopping" and "Back to Cart" links.
- **Rationale**: Maintains visual consistency with the rest of the design system (as seen in `ProductDetailView`'s "Back" button).
- **Alternatives considered**:
    -   *Standard `<a>` tags*: Rejected as they don't match the application's button styling.
    -   *Raw `RouterLink`*: Will be wrapped in or styled as Buttons for better touch targets and aesthetics.

### 3. Layout Strategy
- **Decision**: Use a flex column layout (`min-h-screen flex flex-col`) for page containers, with `flex-grow` on the main content area.
- **Rationale**: This "sticky footer" technique ensures the Footer is always pushed to the bottom of the viewport even when content is sparse (common in empty carts or simple checkout forms), providing a professional look.
- **Alternatives considered**:
    -   *Fixed positioning*: Rejected as it can overlap content on small screens.

## Unknowns & Clarifications
- **Resolved**: No significant technical unknowns. The task relies on standard Vue composition API and existing components.
