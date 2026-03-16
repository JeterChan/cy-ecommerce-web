---
description: "Task list for Member System implementation"
---

# Tasks: Member System

**Input**: Design documents from `/specs/007-member-system/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, research.md

**Tests**: Not explicitly requested, but basic verification steps included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Install backend dependencies (alembic, passlib, pyjwt) in `backend/requirements.txt`
- [x] T002 Install frontend dependencies (axios) in `frontend/package.json`
- [x] T003 Initialize Alembic in `backend/alembic` (if not already init) and configure `backend/alembic.ini`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create `users` table migration script in `backend/alembic/versions/`
- [x] T005 [P] Create `UserEntity` in `backend/src/modules/auth/domain/entity.py`
- [x] T006 [P] Create `IUserRepository` interface in `backend/src/modules/auth/domain/repositories/i_user_repository.py`
- [x] T007 Implement `SqlAlchemyUserRepository` in `backend/src/modules/auth/infrastructure/repositories/sqlalchemy_user_repository.py`
- [x] T008 [P] Update `RegisterUserInputDTO` and `LoginUserInputDTO` in `backend/src/modules/auth/use_cases/dtos.py`
- [x] T009 [P] Setup global Axios instance with base URL in `frontend/src/lib/api.ts`
- [x] T010 [P] Create Pinia `auth` store skeleton in `frontend/src/stores/auth.ts`

**Checkpoint**: Foundation ready - Database schema exists, Repositories ready, Frontend store ready.

---

## Phase 3: User Story 1 - Registration (Priority: P1) 🎯 MVP

**Goal**: Visitors can register a new account.

**Independent Test**: Use Postman/Curl to hit `/auth/register` or use the Frontend Register form.

### Implementation for User Story 1

- [x] T011 [US1] Update `RegisterUserUseCase` logic in `backend/src/modules/auth/use_cases/register.py`
- [x] T012 [US1] Implement Register API endpoint in `backend/src/modules/auth/api/routers.py` (and register router in `main.py`)
- [x] T013 [P] [US1] Create `Register.vue` view in `frontend/src/views/Register.vue`
- [x] T014 [US1] Implement registration action in `frontend/src/stores/auth.ts` calling API
- [x] T015 [US1] Connect `Register.vue` form to `auth` store action

**Checkpoint**: User Story 1 (Registration) should be fully functional.

---

## Phase 4: User Story 2 - Login (Priority: P1)

**Goal**: Members can login and maintain session.

**Independent Test**: Login via UI, check LocalStorage/Cookie for Token, reload page and stay logged in.

### Implementation for User Story 2

- [x] T016 [US2] Update `LoginUserUseCase` logic in `backend/src/modules/auth/use_cases/login.py`
- [x] T017 [US2] Implement Login API endpoint in `backend/src/modules/auth/api/routers.py`
- [x] T018 [US2] Implement `RefreshTokenUseCase` in `backend/src/modules/auth/use_cases/refresh.py`
- [x] T019 [US2] Implement Refresh API endpoint in `backend/src/modules/auth/api/routers.py`
- [x] T020 [P] [US2] Create `Login.vue` view in `frontend/src/views/Login.vue`
- [x] T021 [US2] Implement login action in `frontend/src/stores/auth.ts`
- [x] T022 [US2] Implement Axios interceptor for auto-attaching token and refreshing on 401 in `frontend/src/lib/api.ts`
- [x] T023 [US2] Connect `Login.vue` form to `auth` store action

**Checkpoint**: User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Member Menu & Logout (Priority: P2)

**Goal**: Members see their identity and can logout.

**Independent Test**: Login, see Username in Header, click Logout, verify Token removed.

### Implementation for User Story 3

- [x] T024 [US3] Implement `GetCurrentUser` API endpoint (Me) in `backend/src/modules/auth/api/routers.py`
- [x] T025 [P] [US3] Update `Header` component to show Username/Dropdown when logged in at `frontend/src/components/layout/Header.vue`
- [x] T026 [US3] Implement logout action in `frontend/src/stores/auth.ts` (clear state/storage)
- [x] T027 [US3] Connect Logout button in Header to store action

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T028 [P] Create `ForgotPassword.vue` (UI Only) in `frontend/src/views/ForgotPassword.vue`
- [x] T029 Add "Forgot Password" link to Login page
- [x] T030 Setup Vue Router guards for protected routes in `frontend/src/router/index.ts`
- [x] T031 Run `quickstart.md` validation steps

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup. BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase.
  - **US1 (Register)**: Independent.
  - **US2 (Login)**: Independent (can mock user creation if US1 not done, but better to do after US1).
  - **US3 (Menu)**: Depends on Login (US2) to be testable.

### Parallel Opportunities

- Frontend Views (`Register.vue`, `Login.vue`) can be built in parallel with Backend APIs.
- Backend DTOs and Entities can be defined in parallel.

---

## Implementation Strategy

### MVP First (User Story 1 & 2)

1. Complete Phase 1 & 2 (Setup & Foundation).
2. Complete Phase 3 (Registration) - Verify users created in DB.
3. Complete Phase 4 (Login) - Verify Tokens issued and stored.
4. **STOP and VALIDATE**: Can I register and then login?

### Incremental Delivery

1. Foundation -> Register (US1) -> Login (US2) -> Menu (US3).
2. Each step results in a testable state.
