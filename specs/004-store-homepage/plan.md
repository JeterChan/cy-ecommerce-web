# Implementation Plan: Store Homepage & Navigation

**Branch**: `004-store-homepage` | **Date**: 2025-12-05 | **Spec**: [specs/004-store-homepage/spec.md](spec.md)
**Input**: Feature specification from `/specs/004-store-homepage/spec.md`

## Summary

Implement the store homepage with a navigation bar containing a category dropdown (sourced from product tags), a featured products section (filtered by `is_featured` flag), and a promotional discount information block. Development will use Vue 3, Tailwind CSS, and existing mock services. Special attention to responsive design (hamburger menu), loading states, and error handling as detailed in the updated spec.

## Technical Context

**Language/Version**: TypeScript 5.x (Node.js 18+), Vue.js 3.x
**Primary Dependencies**: Vite 5.x, Tailwind CSS 3.x, shadcn-vue (UI components), Pinia 2.x (State Management), vue-router 4.x
**Storage**: Mock Data (In-memory / LocalStorage for persistence if needed)
**Testing**: Vitest (Unit/Component testing)
**Target Platform**: Web (Responsive: Desktop/Mobile)
**Project Type**: Web Application (Frontend only with Mock Services)
**Performance Goals**: First Contentful Paint < 1.5s (excluding artificial mock delay)
**Constraints**: Must reuse existing `productService` and `mockOrderService` patterns.
**Scale/Scope**: ~3-4 new components, 1 new view, updates to router and services.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **High Quality**: Will use typed interfaces and modular components.
- **Testability**: Services will be mockable; components will be tested for rendering and interaction.
- **MVP First**: Focusing on display and navigation; no complex backend integration yet.
- **Avoid Overdesign**: Using simple mock data instead of full backend for now.
- **Traditional Chinese First**: All UI text and comments will be in Traditional Chinese.

## Project Structure

### Documentation (this feature)

```text
specs/004-store-homepage/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── homepage-api.yaml
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
frontend/src/
├── components/
│   ├── layout/          # New: Navbar (w/ Dropdown), Footer
│   ├── home/            # New: FeaturedProducts (w/ Loading/Empty states), PromotionBlock
│   └── ui/              # Updates: Add DropdownMenu, Card, Skeleton (if missing)
├── views/
│   └── HomeView.vue     # Update: Assemble homepage components
├── services/
│   ├── productService.ts # Update: Add featured support & mock delay handling
│   └── promotionService.ts # New: Promotion data
├── models/
│   ├── Product.ts       # Update: Add featured field
│   └── Promotion.ts     # New: Promotion interface
└── router/
    └── index.ts         # Verify Home route
```

**Structure Decision**: Standard Vue.js feature-based or component-type structure compatible with existing codebase.