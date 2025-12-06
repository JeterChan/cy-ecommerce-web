# Research: Store Homepage & Navigation

**Feature**: `004-store-homepage`
**Date**: 2025-12-05

## Decisions

### 1. Categories Data Source
- **Decision**: Reuse existing `tags` from `productService` as "Categories".
- **Rationale**: The current system uses tags (e.g., '3C', '服飾') which function effectively as categories. Creating a separate "Category" entity at this stage (Mock phase) adds unnecessary complexity.
- **Alternatives Considered**: Creating a dedicated `Category` model and service. Rejected for MVP/Avoid Overdesign.

### 2. Featured Products Logic
- **Decision**: Add an `is_featured` boolean flag to the `Product` model and filter mock data in `productService`.
- **Rationale**: Simple, explicitly controllable way to determine which products appear on the homepage without complex analytics or algorithms.
- **Alternatives Considered**: Random selection, "Newest" selection. Explicit flag allows better control for "Seasonal" requirements.

### 3. Promotion Data
- **Decision**: Create a lightweight `promotionService` returning a static `Promotion` object.
- **Rationale**: The spec requires displaying "Spending Discount" info. While static for now, separating it into a service allows future API integration without refactoring the UI.

### 4. UI Components (shadcn-vue)
- **Decision**: Utilize `shadcn-vue` components (Dropdown Menu, Card) if available, or implement simplified Tailwind versions if "installing" is too disruptive.
- **Rationale**: Project uses `shadcn-vue`. We should maintain consistency.

## Unknowns & Clarifications

- **Resolved**: "Categories" will be mapped to `Product.tags`.
- **Resolved**: Discount logic is "Display Only" for the homepage block (checkout logic is separate in 003, but we display the rule here).
