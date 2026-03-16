# Data Model: Auth Module Enhancement (Clean Architecture)

## 1. Domain Entities (`domain/entities/`)

### 1.1 `UserEntity`
業務邏輯的核心模型。

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | 唯一識別碼。 |
| `username` | String | 唯一使用者名稱。 |
| `email` | EmailAddress (VO) | 唯一信箱位址。 |
| `password` | Password (VO) | 雜湊加密後的密碼。 |
| `is_active` | Boolean | 帳號是否啟用（對應 Email 驗證後）。 |
| `is_verified` | Boolean | Email 是否已驗證。 |
| `deleted_at` | DateTime? | 軟刪除時間戳記。 |

## 2. Persistence Models (`infrastructure/models/`)

### 2.1 `UserDBModel` (SQLAlchemy)
對應資料庫 `users` 表。

| Column | Type | Constraint |
|--------|------|------------|
| `id` | UUID | Primary Key |
| `username` | String | Unique, Not Null |
| `email` | String | Unique, Not Null |
| `password_hash` | String | Not Null |
| `is_active` | Boolean | Default: False |
| `is_verified` | Boolean | Default: False |
| `created_at` | DateTime | Auto: Now |
| `updated_at` | DateTime | Auto: Now/Update |
| `deleted_at` | DateTime | Nullable |

## 3. Cache Model (Redis)

### 3.1 `VerificationToken`
- **Key**: `auth:verify:{token}`
- **Value**: `user_id` (String UUID)
- **TTL**: 86400s (24h)

### 3.2 `PasswordResetToken`
- **Key**: `auth:reset:{token}`
- **Value**: `user_id` (String UUID)
- **TTL**: 3600s (1h)

## 4. State Transitions

1. **Registration**: `is_active=True`, `is_verified=False` -> 發送信件。
2. **Email Verification**: Token 驗證成功 -> `is_verified=True`。
3. **Soft Delete**: 使用者發起刪除 -> `is_active=False`, `deleted_at=Now`, 並視需求清除 Email 以釋放資源。
