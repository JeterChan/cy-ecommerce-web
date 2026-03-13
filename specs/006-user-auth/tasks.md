# Actionable Tasks: User Authentication

**Branch**: `006-user-auth`
**Feature**: User Authentication (Register, Login, Remember Me)
**Total Tasks**: 20

## Phase 1: Setup (Project Initialization)

> **Goal**: Prepare environment and dependencies for implementation.

- [x] T001 Update `backend/requirements.txt` with dependencies (FastAPI, SQLAlchemy, Alembic, Pydantic, Passlib, PyJWT)
- [x] T002 Initialize Alembic configuration in `backend/alembic/` and `backend/alembic.ini`
- [x] T003 [P] Configure database connection in `backend/src/infrastructure/database.py` (SQLAlchemy AsyncEngine)

## Phase 2: Foundational (Blocking Prerequisites)

> **Goal**: Establish core security utilities and base models required by all user stories.

- [x] T004 [P] Implement password hashing utilities (Bcrypt) in `backend/src/core/security.py`
- [x] T005 Implement JWT token handling (create/verify) in `backend/src/core/security.py`
- [x] T006 [P] Create base SQLAlchemy model class in `backend/src/infrastructure/models/base.py`

## Phase 3: User Story 1 - User Registration (Priority: P1)

> **Goal**: Allow users to create accounts.
> **Independent Test**: `test_registration_postgresql.py` verifying successful user creation in DB.

- [x] T006.5 [P] [US1] 建立 User Domain Entity 在 `backend/src/modules/auth/domain/entities.py`
- [x] T007 [US1] 建立 User SQLAlchemy Model 在 `backend/src/modules/auth/infrastructure/models/user.py`
- [x] T008 [P] [US1] 定義 User Pydantic Schemas:
  - API Schemas 在 `backend/src/modules/auth/api/schemas.py`
  - Use Case DTOs 在 `backend/src/modules/auth/use_cases/dtos.py`
- [x] T009 [US1] Generate Alembic migration for User table and apply it (`b53b28ada021_init_user_table.py`)
- [x] T010 [US1] Implement UserRepository `create` method in `backend/src/modules/auth/infrastructure/repositories/user_repository.py`
- [x] T011 [US1] Implement RegisterUserUseCase logic in `backend/src/modules/auth/use_cases/register.py` (採用 Clean Architecture，使用 Use Case 而非 Service)
- [x] T012 [US1] Create Registration API endpoint `POST /api/v1/auth/register` in `backend/src/modules/auth/api/router.py`
- [x] T013 [P] [US1] Create integration test for registration:
  - Unit Tests: `backend/tests/unit/test_register_use_case.py` (18 tests passed ✅)
  - Integration Tests: `backend/tests/integration/test_registration_postgresql.py`

## Phase 4: User Story 2 - User Login (Priority: P1)

> **Goal**: Authenticate users and issue JWT access tokens.
> **Independent Test**: `test_login.py` verifying token receipt on valid credentials.

- [x] T014 [US2] Define Token Pydantic schemas:
  - API Schemas 在 `backend/src/modules/auth/api/schemas.py`
  - Use Case DTOs 在 `backend/src/modules/auth/use_cases/dtos.py`
- [x] T015 [US2] Implement UserRepository `get_by_email` method in `backend/src/modules/auth/infrastructure/repositories/user_repository.py`
- [x] T016 [US2] Implement LoginUserUseCase logic in `backend/src/modules/auth/use_cases/login.py` (採用 Clean Architecture)
- [x] T017 [US2] Create Login API endpoints:
  - `POST /api/v1/auth/login` in `backend/src/modules/auth/api/router.py`
  - `GET /api/v1/auth/users/me` in `backend/src/modules/auth/api/router.py`

## Phase 5: User Story 3 - Remember Me (Priority: P2)

> **Goal**: Extend session validity using Refresh Tokens.
> **Independent Test**: `test_refresh.py` verifying new access token generation from refresh token.

- [ ] T018 [US3] Update Token schemas and Use Cases to support Refresh Tokens (generate/verify):
  - DTOs 在 `backend/src/modules/auth/use_cases/dtos.py`
  - Security utilities 在 `backend/src/core/security.py`
- [ ] T019 [US3] Create Refresh Token endpoint and update Login to handle `remember_me`:
  - `POST /api/v1/auth/refresh` in `backend/src/modules/auth/api/router.py`
  - Update LoginUserUseCase to support remember_me parameter

## Final Phase: Polish

> **Goal**: Finalize and verify the feature.

- [ ] T020 Configure global exception handlers for Auth errors in `backend/src/main.py`

## Dependencies

1. **Setup** (T001-T003) MUST complete before **Foundational**.
2. **Foundational** (T004-T006) MUST complete before **User Story 1**.
3. **User Story 1** (T007-T013) establishes the User model/repo, which **User Story 2** depends on.
4. **User Story 2** (T014-T017) establishes the Token logic, which **User Story 3** extends.

## Implementation Strategy

- **MVP Scope**: Complete Phases 1, 2, 3, and 4. This provides full functional Register/Login.
- **Incremental Delivery**: Deliver US1 (Register) first, verify database creation. Then deliver US2 (Login) to enable frontend integration.
- **Parallelism**: Schemas (T008, T014) and Models (T007) can often be written in parallel with utility functions (T004, T005), but strict sequential execution is safer to avoid circular imports.
