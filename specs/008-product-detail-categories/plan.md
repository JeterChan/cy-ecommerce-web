# Implementation Plan - Sidebar Category Navigation

**Feature**: Sidebar Category Navigation on Product Detail Page
**Branch**: `008-product-detail-categories`
**Spec**: [spec.md](spec.md)
**Status**: Phase 1 (Design Complete)

## Technical Context

- **Frontend**: Vue 3 + Pinia + Tailwind CSS.
- **Backend**: Python (FastAPI) exists but currently only handles Auth. Product data is **completely mocked** in `frontend/src/services/productService.ts`.
- **Current Data**: Products use a simple `tags: string[]` array. There is no formal "Category" entity with hierarchy in the code.
- **Challenge**: The spec requires a hierarchical category list (implied by "sidebar category list" and "ParentID" in spec entities), but the current data is flat tags.
- **Strategy**: 
  - Create a new `CategoryService` (mocked) to define a proper hierarchical category structure (ID, Name, ParentID).
  - Map existing product `tags` to these new Categories (or update the mock products to use Category IDs).
  - Implement the Sidebar Component in Vue.
  - Update `ProductDetailView` to include the sidebar.

## Constitution Check

- [x] **High Quality**: Will use a dedicated Service and Component structure, typed with TypeScript interfaces.
- [x] **Testability**: The `CategoryService` will be testable. The Component will be testable with Vue Test Utils.
- [x] **MVP First**: Will use Mock data to deliver the *experience* and *functionality* without blocking on a full backend build-out.
- [x] **Avoid Overdesign**: Will not build a complex backend catalog system yet; just enough frontend logic to support the feature.
- [x] **Traditional Chinese First**: All UI text and comments will be in Traditional Chinese.

## Gates

- [x] **Design Gate**: Spec is clear. Plan addresses the data gap (Mock vs Real).
- [x] **Research Gate**: Defined mock data structure and layout strategy in `research.md`.
- [x] **Tech Gate**: Vue 3 implementation is standard.

## Phase 0: Outline & Research

### Research Questions

- [x] **RQ1**: How to map existing `tags` to a hierarchical structure?
  - *Decision*: Create a standalone `mockCategories` array in a new `CategoryService`. For this MVP, we might just map the flat tags to top-level categories, OR create a proper tree and assign products to leaf nodes.
  - *Refinement*: To support "User Story 2: Visualize Current Category Context" (highlight active), products need to know their category. I will update `mockProducts` to have a `categoryId` or keep using `tags` but map the *first* tag to a Category.

### Proposed Architecture

1.  **`src/models/Category.ts`**: Define `Category` interface.
2.  **`src/services/categoryService.ts`**: Mock implementation returning a tree or list of categories.
3.  **`src/components/layout/CategorySidebar.vue`**: New component.
4.  **`src/views/ProductDetailView.vue`**: Refactor layout to Grid/Flex to accommodate sidebar.

### Tasks

1.  [Research] Define the `Category` data model and Mock Data content.
2.  [Research] Determine the layout strategy (Grid vs Flex) for the PDP to ensure responsiveness.

## Phase 1: Design & Contracts

### Data Model (`data-model.md`)

- **Category**: `id`, `name`, `parentId` (optional), `slug`.
- **Product Update**: Add `categoryId` (optional, for linking) or helper to find category from tags.

### API Contracts (`contracts/`)

- Since it's internal Mock API:
  - `getTree()`: Returns hierarchical list.
  - `getById(id)`: Returns single category.

### Agent Context

- Update `gemini.md` with "Category Service" and "Mock Data" patterns.

## Phase 2: Implementation (Draft)

1.  Create `Category` model and service.
2.  Create `CategorySidebar` component.
3.  Update `ProductDetailView` layout.
4.  Add mobile responsiveness (collapsible or stacked).
5.  Verify "Active State" logic.
