# Research: Auth Module Enhancement

## 1. Decision: Clean Architecture Alignment
目前的 `auth` 模組已具備 Clean Architecture 雛形。我們將維持此結構並擴展以下組件：

- **Domain Layer**: 
  - 更新 `UserEntity` 以包含 `is_verified` 與 `deleted_at`。
  - 在 `IUserRepository` 中新增必要的查詢與更新接口。
- **Application Layer**:
  - 新增 `Use Cases`: `VerifyEmail`, `ForgotPassword`, `ResetPassword`, `ChangePassword`, `DeleteAccount` (需密碼驗證)。
  - 復用或擴展現有的 `EmailService` 接口。
- **Infrastructure Layer**:
  - 在 `UserRepository` (SQLAlchemy) 中實作軟刪除邏輯。
  - 在 `TokenManager` (Redis) 中實作具時效性的驗證/重設 Token 存取。
  - 在 `BrevoService` 中新增郵件發送實作。
- **Presentation Layer**:
  - 更新 FastAPI 路由與 Pydantic Schemas。

## 2. Decision: Technical Stack & Integration
- **Python 3.12**: 使用其型別標記與效能改進。
- **FastAPI**: 用於建立高效的 API 端點。
- **PostgreSQL (SQLAlchemy)**: 處理持久化資料與軟刪除。
- **Redis**: 處理具時效性的 Token。
- **Celery**: 非同步處理郵件發送。

## 3. Rationale
- **Clean Architecture**: 確保業務邏輯與基礎設施（資料庫、郵件服務）解耦，便於測試與未來擴展。
- **Soft Delete**: 使用 `deleted_at` 而非物理刪除，符合電商系統對於審計與資料恢復的需求。
- **Redis Tokens**: Token 存放在 Redis 具備極高的存取速度與自動過期特性，減輕資料庫負擔。

## 4. Alternatives Considered
- **Database Tokens**: 將驗證 Token 存在 PostgreSQL。雖然持久化更好，但會增加資料表膨脹且需要手動清理過期資料。決策：Redis 優先。
- **JWT for Verification**: 使用 JWT 攜帶驗證資訊。雖然 Stateless，但無法輕易撤回 (Revoke)。決策：Redis Token (Stateful) 優先，以支援單次使用與強制失效。
