# 資料模型：驗證系統前端頁面擴展 (Auth Frontend Pages Extension)

## 前端實體 (Entities)

### User Profile (使用者個人資料)
- `email`: string (readonly) - 使用者電子郵件。
- `nickname`: string - 使用者暱稱，必填。
- `phone`: string (optional) - 使用者電話號碼。
- `avatar_url`: string (optional) - 使用者頭像網址。
- `is_verified`: boolean (readonly) - 信箱是否已驗證。
- `created_at`: string (readonly, ISO date) - 帳號建立時間。

### Auth Tokens (驗證憑證)
- `token`: string - 用於重設密碼或信箱驗證的一次性憑證。
- `type`: string - 'RESET' | 'VERIFY'。

## 驗證規則 (Validation Rules - Zod)

### ForgotPasswordSchema
- `email`: email 格式, 必填。

### ResetPasswordSchema
- `password`: 至少 8 位字元，包含大小寫字母與數字。
- `confirm_password`: 必須與 `password` 相同。

### UserProfileUpdateSchema
- `nickname`: 至少 2 位字元, 必填。
- `phone`: 符合台灣手機格式 (09xxxxxxxx) 或留空。

## 狀態轉換 (State Transitions)
- **Email Verification**: `Pending` -> `Verified` (透過 `email-verify` API)。
- **Password Reset**: `Known` -> `Forgot` -> `Reset` (透過 `forgot-password` -> `reset-password` 流程)。
