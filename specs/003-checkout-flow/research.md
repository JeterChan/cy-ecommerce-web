# Research: 建立訂單流程

**Feature**: 建立訂單流程 (003-checkout-flow)
**Status**: Researching
**Created**: 2025-12-05

## Unknowns & Clarifications

### 1. Payment Gateway Integration
- **Context**: The spec requires Credit Card payment support.
- **Unknown**: Which specific payment gateway (ECPay, Stripe, LinePay, etc.) should be used?
- **Decision**: 使用 **Mock Payment Service** for MVP.
- **Rationale**: 
  - 符合 MVP 優先原則，先驗證訂單流程與資料流正確性。
  - 避免初期綁定特定第三方服務，降低開發複雜度。
  - 介面設計將保留擴充性，未來可替換為真實金流 SDK。

### 2. Frontend Technology
- **Context**: "Use existing technology".
- **Findings**: 
  - Framework: **Vue 3** (Composition API)
  - Build Tool: **Vite**
  - State Management: **Pinia**
  - Routing: **Vue Router**
  - Styling: **Tailwind CSS** + **shadcn-vue** (inferred from `radix-vue`, `class-variance-authority`, `lucide-vue-next`)
- **Decision**: 嚴格遵循現有 Vue 3 + Tailwind 技術棧。

## Technology Decisions

### Backend API Design
- **Protocol**: RESTful API
- **Format**: JSON
- **Validation**: Pydantic (Python backend standard) or similar for payload validation.

### State Management (Frontend)
- **Store**: Use a dedicated `useCheckoutStore` in Pinia.
- **Persistance**: 考慮使用 `localStorage` 暫存未完成的訂單資訊，防止重新整理後資料遺失 (UX improvement).

### Validation Strategy
- **Frontend**: 使用 VeeValidate 或自行封裝的 composables 進行即時欄位驗證 (Zod is often used with Vue/TS, need to check if installed, otherwise standard regex).
- **Backend**: 二次驗證所有傳入資料，確保資料完整性。

## Alternatives Considered

- **Multi-step Form vs Single Page Checkout**:
  - **Decision**: **Single Page Checkout** (or clear steps on one page).
  - **Rationale**: 減少頁面跳轉，提升轉換率 (SC-001 < 3 mins goal).

## Action Items

- [ ] Define `Order` and `ShippingInfo` schemas in `data-model.md`.
- [ ] Create OpenAPI contract for `POST /api/orders`.
- [ ] Implement `useCheckoutStore` with state for steps (Cart -> Info -> Payment -> Review).
