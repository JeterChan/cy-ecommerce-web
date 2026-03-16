# Implementation Plan: 建立訂單相關的前端頁面 (Create Order Frontend Pages)

**Branch**: `012-order-frontend-ui` | **Date**: 2026-02-21 | **Spec**: [specs/012-order-frontend-ui/spec.md](../spec.md)
**Input**: Feature specification from `/specs/012-order-frontend-ui/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement frontend pages for viewing order history and order details. This involves creating new Vue components, setting up routes, managing state with Pinia, and integrating with the backend Order Service via a new `OrderService` (using Axios). The UI will adhere to the existing design system (Tailwind CSS + shadcn/ui).

## Technical Context

**Language/Version**: TypeScript 5.x, Vue 3.5
**Primary Dependencies**: Axios, Pinia, Vue Router, Tailwind CSS, shadcn/ui (radix-vue)
**Storage**: N/A (Frontend consumes API; Backend uses PostgreSQL/Redis)
**Testing**: Vitest, @vue/test-utils
**Target Platform**: Web Browser (Modern)
**Project Type**: Web Application
**Performance Goals**: Order list load < 1.5s, Detail view instant navigation if cached.
**Constraints**: Must match existing UI style. Must handle API errors gracefully.
**Scale/Scope**: ~3 new views, ~2-3 reusable components, 1 new service, 1 new store.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **High Quality**: Code will be typed, componentized, and follow Vue 3 best practices.
- [x] **Testability**: Service logic and key components will be tested with Vitest.
- [x] **MVP First**: Focus on List, Detail, and Cancel functionality. No advanced filtering initially.
- [x] **Avoid Overdesign**: Use simple REST calls, store data in Pinia only when necessary for UX.
- [x] **Traditional Chinese**: UI and comments will use Traditional Chinese.

## Project Structure

### Documentation (this feature)

```text
specs/012-order-frontend-ui/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/
│   │   └── order/
│   │       ├── OrderCard.vue
│   │       ├── OrderItemList.vue
│   │       └── OrderStatusBadge.vue
│   ├── views/
│   │   ├── OrderListView.vue
│   │   └── OrderDetailView.vue
│   ├── services/
│   │   ├── orderService.ts
│   │   └── mockOrderService.ts (Updated or kept for ref)
│   ├── stores/
│   │   └── useOrderStore.ts
│   ├── router/
│   │   └── index.ts (Update)
│   └── types/
│       └── order.ts (Update)
└── tests/
    ├── components/
    │   └── order/
    └── services/
        └── orderService.spec.ts
```

**Structure Decision**: Standard Vue 3 application structure within the `frontend` directory. Service layer isolates API communication.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A       |            |                                     |