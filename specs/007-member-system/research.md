# Research: Member System

**Feature**: Member System (Auth)
**Status**: Research Complete

## Decisions

### 1. Authentication Strategy
- **Decision**: JWT (JSON Web Token) with Access/Refresh Token pattern.
- **Rationale**: 
  - Stateless authentication scales well.
  - Spec requirement explicitly mentions JWT.
  - "Remember Me" implemented via Refresh Token (7 days default, extensible).
- **Implementation**:
  - `access_token`: Short-lived (30 mins), stored in memory (Pinia store).
  - `refresh_token`: Long-lived (7 days), stored in HTTPOnly cookie or Secure LocalStorage (MVP: LocalStorage for simplicity as per common SPA patterns, though Cookie is more secure. *Correction*: For MVP Vue SPA, LocalStorage is acceptable if XSS protected, but HttpOnly Cookie is best practice. Given "MVP First" and typical Vue setups, LocalStorage is easier to implement without complex CORS/Cookie logic on backend first. Will stick to Response Body return -> LocalStorage for MVP, upgrading to Cookies later if needed).

### 2. Frontend Tech Stack
- **Framework**: Vue 3 + Vite (Existing).
- **State Management**: Pinia (Existing).
- **UI Library**: Tailwind CSS + Headless UI (Radix Vue) (Existing).
- **HTTP Client**: Axios (Need to add).
  - **Rationale**: Better interceptor support than native fetch for automatic token attachment and refresh logic.

### 3. Password Security
- **Algorithm**: bcrypt (via `passlib`).
- **Complexity**: 
  - Min 8 chars.
  - At least 1 Uppercase.
  - At least 1 Lowercase.
  - At least 1 Digit.
  - At least 1 Special Character (New requirement to add).

### 4. Database Schema
- **Table**: `users`
- **Fields**: 
  - `id` (UUID, PK)
  - `username` (String, Unique)
  - `email` (String, Unique)
  - `password_hash` (String)
  - `is_active` (Boolean)
  - `created_at` (Timestamp)
  - `updated_at` (Timestamp)
- **Migration**: Alembic (Need to init).

### 5. Forgot Password
- **Decision**: MVP will provide the Page and Route, but backend email sending might be mocked/logged initially if SMTP is not configured.
- **Rationale**: Spec focuses on UI flow ("Redirect to page"). Functional email delivery requires SMTP credentials which might not be available in dev.

## Unknowns & Clarifications (Resolved)

- **Q**: Existing Auth Code?
  - **A**: Yes, `backend/src/modules/auth` has `use_cases` and `domain` entities. Needs `dtos.py` update and `repository` implementation.
- **Q**: Frontend HTTP Client?
  - **A**: None found. Will implement `src/lib/api.ts` using Axios.

## Action Items

1.  **Backend**: Update `RegisterUserInputDTO` regex for special characters.
2.  **Backend**: Create Alembic migration for `users` table.
3.  **Frontend**: Install `axios`.
4.  **Frontend**: Implement `useAuthStore` in Pinia.
5.  **Frontend**: Create Login/Register/Forgot views.
