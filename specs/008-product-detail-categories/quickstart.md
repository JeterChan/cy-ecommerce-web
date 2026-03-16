# Quickstart: Product Detail Categories

**Branch**: `008-product-detail-categories`

## Overview

This feature adds a sidebar to the Product Detail Page displaying a list of product categories. It introduces a new `Category` entity and service (mocked) to support this navigation.

## Setup

1.  **Frontend Only**: This feature changes only the `frontend/` directory.
2.  **Dependencies**: No new npm packages required.

## Running

1.  Start the frontend:
    ```bash
    cd frontend
    npm run dev
    ```
2.  Navigate to a product detail page (e.g., click a product on home page).
3.  Observe the sidebar on the left.

## Key Components

- `frontend/src/services/categoryService.ts`: Manage category data.
- `frontend/src/components/layout/CategorySidebar.vue`: The new sidebar UI.
- `frontend/src/views/ProductDetailView.vue`: Updated layout.
