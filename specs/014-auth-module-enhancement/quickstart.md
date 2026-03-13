# Quickstart: Auth Module Enhancement

## 1. Development Environment Setup
確保後端服務與基礎設施 (PostgreSQL, Redis) 正在運行。

```bash
cd backend
# 啟動開發環境
docker-compose up -d
```

## 2. Verify Redis Connection
確保 API 可以存取 Redis 用於 Token 儲存。

```bash
docker-compose exec redis redis-cli ping
# 預期回應: PONG
```

## 3. Run Tests
執行單元測試與整合測試。

```bash
docker-compose exec api pytest tests/modules/auth/
docker-compose exec api pytest tests/integration/test_verification_flow.py
docker-compose exec api pytest tests/integration/test_password_reset.py
docker-compose exec api pytest tests/integration/test_profile_update.py
docker-compose exec api pytest tests/integration/test_account_deletion.py
```

## 4. Local API Testing (Examples)

### 註冊與驗證 (US1)
1. **註冊**: `POST /api/v1/auth/register`
   - Body: `{"username": "jeter", "email": "jeter@example.com", "password": "password123"}`
2. **驗證**: `GET /api/v1/auth/verify-email?token=<token_from_redis>`
   - 可在 Redis 查詢: `docker-compose exec redis redis-cli KEYS "auth:verify:*"`

### 忘記密碼 (US2)
1. **請求重設**: `POST /api/v1/auth/forgot-password`
   - Body: `{"email": "jeter@example.com"}`
2. **重設密碼**: `POST /api/v1/auth/reset-password`
   - Body: `{"token": "<token_from_redis>", "new_password": "new_password123"}`

### 個人檔案與安全性 (US3)
1. **變更使用者名稱**: `PATCH /api/v1/auth/me/profile` (需 Bearer Token)
   - Body: `{"username": "new_jeter"}`
2. **變更密碼**: `POST /api/v1/auth/me/change-password` (需 Bearer Token)
   - Body: `{"old_password": "password123", "new_password": "super_secure_pass"}`

### 帳號刪除 (US4)
1. **刪除帳號**: `DELETE /api/v1/auth/me` (需 Bearer Token)
   - Body: `{"password": "super_secure_pass"}`
