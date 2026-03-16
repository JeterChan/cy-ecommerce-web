# Tasks: Auth Module Enhancement

**Input**: Design documents from `/specs/014-auth-module-enhancement/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment verification

- [X] T001 Verify backend development environment (Docker/Redis/PostgreSQL)
- [X] T002 [P] Check existing Celery worker configuration in `backend/src/infrastructure/celery_app.py`
- [X] T003 [P] Verify Brevo email service API keys in `.env`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data structures and interfaces required by all user stories

- [ ] T004 Create Alembic migration for `users` table fields (`is_verified`, `deleted_at`) in `backend/alembic/versions/` (Skipped per user request in dev phase)
- [X] T005 Update `UserEntity` to include `is_verified` and `deleted_at` in `backend/src/modules/auth/domain/entities/UserEntity.py`
- [X] T006 Update `UserDBModel` to include new columns in `backend/src/modules/auth/infrastructure/models/user.py`
- [X] T007 [P] Extend `IUserRepository` interface with soft delete and verification methods in `backend/src/modules/auth/domain/repositories/i_user_repository.py`
- [X] T008 [P] Implement `UserRepository` updates for soft delete in `backend/src/modules/auth/infrastructure/repositories/user_repository.py`
- [X] T009 [P] Implement `TokenManager` methods for 24h verification and 1h reset tokens in `backend/src/infrastructure/redis/token_manager.py`
- [X] T010 [P] Define `IEmailService` methods for verification and reset emails in `backend/src/infrastructure/email/interface.py`
- [X] T011 [P] Implement `BrevoService` email sending for auth in `backend/src/infrastructure/email/brevo_service.py`

**Checkpoint**: Foundation ready - User Story implementation can begin

---

## Phase 3: User Story 1 - 註冊與信箱驗證 (Priority: P1) 🎯 MVP

**Goal**: Users can register, receive a verification email, and verify their account to login.

**Independent Test**: Register a new user -> Receive token in Redis/Logs -> Call verify API -> User `is_verified` becomes true.

### Tests for User Story 1 (Requested in Plan)

- [X] T012 [P] [US1] Unit test for verification token generation in `backend/tests/unit/modules/auth/test_tokens.py`
- [X] T013 [US1] Integration test for registration-to-verification flow in `backend/tests/integration/test_verification_flow.py`

### Implementation for User Story 1

- [X] T014 [US1] Create `VerifyEmailUseCase` in `backend/src/modules/auth/application/use_cases/verify_email.py`
- [X] T015 [US1] Modify `RegisterUseCase` to trigger verification email task in `backend/src/modules/auth/use_cases/register.py`
- [X] T016 [US1] Implement `verify_email` endpoint in `backend/src/modules/auth/presentation/routes.py`
- [X] T017 [US1] Update `LoginUseCase` to reject unverified users in `backend/src/modules/auth/use_cases/login.py`
- [X] T018 [US1] Add logging for registration and verification events in `backend/src/modules/auth/use_cases/register.py` and `backend/src/modules/auth/application/use_cases/verify_email.py`

**Checkpoint**: User Story 1 functional

---

## Phase 4: User Story 2 - 忘記密碼與重設流程 (Priority: P1)

**Goal**: Users can request a password reset and set a new password using a secure token.

**Independent Test**: Request reset -> Get token -> Reset password with token -> Login with new password.

### Tests for User Story 2 (Requested in Plan)

- [X] T019 [P] [US2] Unit test for reset token expiry in `backend/tests/unit/modules/auth/test_tokens.py`
- [X] T020 [US2] Integration test for password reset journey in `backend/tests/integration/test_password_reset.py`

### Implementation for User Story 2

- [X] T021 [US2] Create `ForgotPasswordUseCase` in `backend/src/modules/auth/application/use_cases/forgot_password.py`
- [X] T022 [US2] Create `ResetPasswordUseCase` in `backend/src/modules/auth/application/use_cases/reset_password.py`
- [X] T023 [US2] Implement `forgot_password` and `reset_password` endpoints in `backend/src/modules/auth/presentation/routes.py`
- [X] T024 [US2] Add logging for password reset requests and successful resets (security audit)

**Checkpoint**: User Story 2 functional

---

## Phase 5: User Story 3 - Profile 頁面變更資訊 (Priority: P2)

**Goal**: Logged-in users can update their username and change their password.

**Independent Test**: Change username -> Verify uniqueness -> Change password -> Login with new password.

### Tests for User Story 3

- [X] T025 [P] [US3] Integration test for profile update and password change in `backend/tests/integration/test_profile_update.py`

### Implementation for User Story 3

- [X] T026 [US3] Create `ChangePasswordUseCase` in `backend/src/modules/auth/application/use_cases/change_password.py`
- [X] T027 [US3] Update `UpdateProfileUseCase` to handle `username` changes in `backend/src/modules/auth/application/use_cases/update_profile.py`
- [X] T028 [US3] Implement `change_password` endpoint in `backend/src/modules/auth/presentation/routes.py`
- [X] T029 [US3] Add logging for username change and password update operations (security audit)

**Checkpoint**: User Story 3 functional

---

## Phase 6: User Story 4 - 帳號刪除 (Priority: P3)

**Goal**: Users can soft-delete their account after password verification.

**Independent Test**: Call delete API with wrong password (fail) -> Call with correct password (success) -> Cannot login anymore.

### Tests for User Story 4

- [X] T030 [P] [US4] Integration test for account deletion with password verification in `backend/tests/integration/test_account_deletion.py`

### Implementation for User Story 4

- [X] T031 [US4] Modify `DeleteAccountUseCase` to require password verification in `backend/src/modules/auth/application/use_cases/delete_account.py`
- [X] T032 [US4] Implement `delete_account` endpoint in `backend/src/modules/auth/presentation/routes.py`
- [X] T033 [US4] Update `get_current_user` dependency to filter out soft-deleted users in `backend/src/core/security.py`
- [X] T034 [US4] Add logging for account deletion operations (security audit)

---

## Phase N: Polish & Cross-Cutting Concerns

- [X] T035 [P] Update `specs/014-auth-module-enhancement/quickstart.md` with final API examples
- [X] T036 Run full test suite `pytest backend/tests/modules/auth/`
- [X] T037 [P] Security audit: Ensure all tokens are single-use and properly revoked from Redis

---

## Dependencies & Execution Order

1. **Foundational (Phase 2)**: MUST be completed first.
2. **User Story 1 (P1)**: High priority, can be done in parallel with US2 after Phase 2.
3. **User Story 2 (P1)**: High priority, can be done in parallel with US1 after Phase 2.
4. **User Story 3 (P2)**: Medium priority, depends on existing Profile infrastructure.
5. **User Story 4 (P3)**: Lower priority, depends on Phase 2 soft delete fields.

### Parallel Opportunities
- T007, T008, T009, T010, T011 (Infrastructure implementations) can run in parallel.
- Once Phase 2 is done, Phase 3 (US1) and Phase 4 (US2) can be implemented simultaneously.
- Unit tests (T012, T019) can be written in parallel.

---

## Implementation Strategy
- **MVP First**: Focus on completing US1 and US2 (Verification & Reset).
- **Clean Architecture**: Strictly separate Domain Entity, Use Case, and Presentation Route.
- **Verification**: Each story must have a working manual/automated test before moving to the next.
