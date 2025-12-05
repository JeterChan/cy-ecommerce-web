# Implementation Plan: Shopping Cart

**Branch**: `002-shopping-cart` | **Date**: 2025-12-03 | **Spec**: [specs/002-shopping-cart/spec.md](../spec.md)
**Input**: Feature specification from `/specs/002-shopping-cart/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a client-side shopping cart using Pinia for state management. Features include adding items from the product detail page with a quantity selector, a persistent cart store (LocalStorage), a navbar cart icon with a badge, and a dedicated cart page to view and manage items.

## Technical Context

**Language/Version**: TypeScript 5.x (Node.js 18+)
**Primary Dependencies**: Vue.js 3.x, Vite 5.x, Tailwind CSS 3.x, shadcn-vue, Pinia 2.x
**Storage**: LocalStorage (Client-side persistence)
**Testing**: Vitest, @vue/test-utils
**Target Platform**: Modern Web Browsers
**Project Type**: Web Application (Frontend)
**Performance Goals**: Cart operations < 50ms
**Constraints**: Must support Traditional Chinese UI. No backend API for cart in this phase.
**Scale/Scope**: Client-side only, ~20 items max recommended.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **High Quality**: Using Pinia for type-safe state management.
- **Testability**: Logic in Pinia stores is easily unit testable.
- **MVP First**: Client-side only cart avoids complex backend synchronization for now.
- **Avoid Overdesign**: Simple `watch` for persistence instead of heavy plugins.
- **Traditional Chinese**: UI text will be TC.

## Project Structure

### Documentation (this feature)

```text
specs/002-shopping-cart/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/
│   │   ├── cart/        # CartItem.vue, CartSummary.vue
│   │   ├── ui/          # QuantitySelector.vue
│   ├── models/          # Cart.ts
│   ├── stores/          # cart.ts (Pinia store)
│   ├── views/           # CartView.vue
│   └── App.vue          # Update Navbar
```

**Structure Decision**: Standard Vue+Pinia structure. New `stores` directory for state management.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (None)    |            |                                     |