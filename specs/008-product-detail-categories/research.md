# Research: Sidebar Category Navigation

**Feature**: `008-product-detail-categories`
**Date**: 2026-01-22

## Decision Log

### 1. Data Source Strategy
- **Context**: The backend currently only supports Auth. Product data is mocked in `productService.ts` using a flat `tags` array.
- **Problem**: The spec requires a hierarchical category list (e.g., Parent/Child relationships) and linking products to specific categories for highlighting. Flat tags are insufficient.
- **Decision**: **Create a dedicated `CategoryService` with Mock Data.**
  - We will strictly type the data with a `Category` interface.
  - We will migrate or map the existing `mockProducts` to reference these categories (e.g., add a `categoryId` field to products in the mock, or map the first tag to a category name).
  - **Rationale**: This adheres to the "High Quality" principle by establishing a proper domain model (even if mocked) rather than hacking string arrays. It paves the way for a real backend later.
  - **Alternatives Considered**: 
    - *Use existing tags*: Rejected because it doesn't support hierarchy (ParentID) required by the spec's intent.
    - *Build Backend*: Rejected as out of scope for this specific frontend UI feature.

### 2. Responsive Layout Strategy
- **Context**: Adding a sidebar to an existing full-width Product Detail Page.
- **Problem**: Needs to look good on Desktop (Sidebar + Content) and Mobile (Stacked or Collapsible).
- **Decision**: **Use CSS Grid for the Page Layout.**
  - Desktop: `grid-template-columns: 250px 1fr;`
  - Mobile: `grid-template-columns: 1fr;` (Sidebar stacks above or below, or becomes a drawer).
  - **Rationale**: CSS Grid provides the most robust 2-column layout control without fighting float/flex behaviors.
  - **Mobile Detail**: For P3 (Mobile), we will initially stack the category list *below* the main product info or use a simple "Show Categories" toggle to avoid pushing the product too far down.

### 3. "Active" Category Logic
- **Context**: Spec requires highlighting the current product's category.
- **Decision**:
  - Add `categoryId` to the `Product` interface (optional).
  - In `mockProducts`, populate this `categoryId` for test data.
  - The Sidebar will accept `activeCategoryId` as a prop.

## Technical Details

- **New Files**:
  - `frontend/src/models/Category.ts`
  - `frontend/src/services/categoryService.ts`
  - `frontend/src/components/layout/CategorySidebar.vue`
- **Modified Files**:
  - `frontend/src/models/Product.ts` (add `categoryId`)
  - `frontend/src/views/ProductDetailView.vue` (layout changes)
