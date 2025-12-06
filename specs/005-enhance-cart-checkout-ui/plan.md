# Implementation Plan: Enhance Cart and Checkout UI Layout

**Branch**: `005-enhance-cart-checkout-ui` | **Date**: 2025-12-06 | **Spec**: [specs/005-enhance-cart-checkout-ui/spec.md](spec.md)
**Input**: Feature specification from `/specs/005-enhance-cart-checkout-ui/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature aims to improve UI consistency by integrating the global `Navbar` and a new reusable `Footer` component into the Shopping Cart and Checkout pages. It also adds specific navigation controls ("Continue Shopping" and "Back to Cart") to enhance user flow. Technical approach involves extracting the footer from `HomeView` into a shared component, updating layouts, and adding Vue Router links.

## Technical Context

**Language/Version**: TypeScript 5.x, Vue.js 3.x (Node.js 18+)  
**Primary Dependencies**: Vue Router 4.x, Pinia 2.x, Tailwind CSS 3.x, shadcn-vue, lucide-vue-next  
**Storage**: LocalStorage (for cart persistence, client-side)  
**Testing**: Vitest (Unit/Component), Playwright (E2E - if applicable)  
**Target Platform**: Web Browsers (Modern)  
**Project Type**: web  
**Performance Goals**: Consistent UI rendering, no significant layout shifts (CLS), responsive design < 300ms interaction delay.  
**Constraints**: Must use existing `shadcn-vue` components where applicable. Must adhere to "Traditional Chinese First" principle.  
**Scale/Scope**: Frontend-only changes, affecting 3 main views (Home, Cart, Checkout) and layout components.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. 高品質 (High Quality)**: Adhering to component reusability (extracting Footer) improves maintainability.
- [x] **II. 可測試性 (Testability)**: Changes are visual and navigational, testable via unit tests (mounting components) and e2e flows.
- [x] **III. 最小可行性產品 (MVP First)**: Focuses only on layout consistency and basic navigation links, no complex new features.
- [x] **IV. 避免過度設計 (Avoid Overdesign)**: Reusing existing Navbar and creating a simple shared Footer. No new layout system or framework introduced.
- [x] **V. 正體中文優先 (Traditional Chinese First)**: All new UI text (buttons, links) will be in Traditional Chinese as per spec.

## Project Structure

### Documentation (this feature)

```text
specs/005-enhance-cart-checkout-ui/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Navbar.vue       # Existing
│   │   │   └── Footer.vue       # New (Extracted)
│   │   └── ui/                  # shadcn-vue components
│   ├── views/
│   │   ├── HomeView.vue         # Update to use shared Footer
│   │   ├── CartView.vue         # Update layout & nav
│   │   └── CheckoutPage.vue     # Update layout & nav
└── tests/
```

**Structure Decision**: Standard Vue.js feature/component structure. Extracting `Footer` to `components/layout` alongside `Navbar` is the idiomatic choice for global layout elements.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | | |