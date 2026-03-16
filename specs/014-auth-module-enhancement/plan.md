# Implementation Plan: Auth Module Enhancement

**Feature Branch**: `014-auth-module-enhancement`  
**Created**: 2026-03-10  
**Status**: Draft  
**Reference**: [spec.md](./spec.md)

## 1. Technical Context

### 1.1 Stack
- **Language**: Python 3.12
- **Framework**: FastAPI
- **Database**: PostgreSQL (SQLAlchemy + Alembic)
- **Cache**: Redis
- **Background Jobs**: Celery
- **Architecture**: Clean Architecture (Domain, Application, Infrastructure, Presentation)

### 1.2 Dependencies
- `redis`: Python Redis Client.
- `celery`: Task Queue.
- `passlib`: Password Hashing (Existing).
- `python-jose`: JWT Tokens (Existing).
- `brevo-python`: Email Sending (Existing).

## 2. Constitution Check

- [x] **高品質**: 使用強型別 (Type Hints) 與 Clean Architecture 確保代碼清晰。
- [x] **可測試性**: 業務邏輯集中於 Use Cases，便於單元測試。
- [x] **MVP 優先**: 優先實作 P1 任務（驗證與重設）。
- [x] **避免過度設計**: 復用現有的 Email 與 Redis 基礎設施。
- [x] **正體中文優先**: 文件與註釋採用正體中文。

## 3. Implementation Phases

### Phase 1: Foundation (Data & Infra)
- [ ] **Database Migration**: 新增 `is_verified` 與 `deleted_at` 欄位。
- [ ] **Domain Entity**: 更新 `UserEntity` 類別。
- [ ] **Redis Repository**: 擴展 `TokenManager` 以處理具時效性的單次 Token。
- [ ] **Email Interface**: 確保 `IEmailService` 具備發送驗證與重設郵件的方法。

### Phase 2: Core Logic (Application & Use Cases)
- [ ] **P1: Register & Verify**:
  - `RegisterUseCase`: 修改註冊流程，觸發 `SendVerificationEmail` 任務。
  - `VerifyEmailUseCase`: 驗證 Redis Token 並更新 `is_verified`。
- [ ] **P1: Forgot & Reset**:
  - `RequestPasswordResetUseCase`: 驗證 Email 並發送 `ResetToken`。
  - `ResetPasswordUseCase`: 驗證 Token 並透過 `Password` VO 更新密碼。

### Phase 3: Profile & Security (Application)
- [ ] **P2: Profile Updates**:
  - `UpdateProfileUseCase`: 允許變更 `username`。
  - `ChangePasswordUseCase`: 驗證舊密碼並更新新密碼。
- [ ] **P3: Account Deletion**:
  - `DeleteAccountUseCase`: 驗證密碼並執行軟刪除。

### Phase 4: API & Presentation
- [ ] **FastAPI Routers**: 實作 `openapi.yaml` 中定義的新端點。
- [ ] **Middlewares/Dependencies**: 更新現有的 `get_current_user` 以排除未驗證或已刪除的帳號。

### Phase 5: Verification & Testing
- [ ] **Unit Tests**: 單獨測試各個 Use Cases。
- [ ] **Integration Tests**: 測試端到端的流程（使用 Test Redis 與 DB）。

## 4. Risks & Mitigations
- **Email Delivery Failure**: 若郵件發送失敗，使用者無法啟用帳號。
  - *Mitigation*: 實作「重新發送驗證信」按鈕。
- **Token Leakage**: Reset Token 若被截獲。
  - *Mitigation*: 確保 Token 具有極短的時效性（1h）且僅能使用一次。
- **Uniqueness Conflict on Deleted Accounts**: 已刪除的 Email 是否可重新註冊？
  - *Decision*: **可以重新註冊**。若舊帳號的 Email 已從資料庫完全移除（或在軟刪除時將 Email 欄位清空/匿名化處理以釋出唯一索引），則該 Email 可供新使用者註冊使用。這確保了資源的重複利用，同時也需要處理舊資料的匿名化。
