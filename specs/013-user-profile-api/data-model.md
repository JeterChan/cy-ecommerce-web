# 資料模型：使用者個人檔案管理 API

## 實體 (Entities)

### 使用者個人檔案 (使用者的擴展)

此功能擴充現有的 `users` 資料表以支援額外的個人檔案資訊。

| 欄位 | 類型 | 必填 | 唯一 | 描述 |
|-------|------|----------|--------|-------------|
| `display_name` | String(100) | 否 | 否 | 使用者偏好的顯示名稱 (預設為 username) |
| `phone_number` | String(20) | 否 | 是 | E.164 格式的電話號碼 |
| `address` | Text | 否 | 否 | 使用者預設地址 (JSON 或字串) |
| `avatar_url` | String(500) | 否 | 否 | 使用者頭像的 URL |
| `bio` | Text | 否 | 否 | 簡短自我介紹 |
| `deleted_at` | DateTime | 否 | 否 | 軟刪除的時間戳記 (啟用時為 NULL) |

## 領域物件 (DTOs)

### UserProfileResponse (DTO)
代表使用者的個人檔案視圖。
- `id`: UUID
- `username`: String
- `email`: EmailStr
- `display_name`: Optional[String]
- `phone_number`: Optional[String]
- `avatar_url`: Optional[String]
- `bio`: Optional[String]
- `created_at`: DateTime
- `updated_at`: DateTime

### UpdateProfileRequest (DTO)
用於更新個人檔案欄位的輸入。
- `display_name`: Optional[String(1-100)]
- `phone_number`: Optional[String(E.164)]
- `address`: Optional[String]
- `avatar_url`: Optional[HttpUrl]
- `bio`: Optional[String(Max 500 chars)]

### EmailChangeRequest (DTO)
用於更改電子郵件的輸入。
- `new_email`: EmailStr
- `password`: String (用於確認所有權)

### VerifyEmailChangeRequest (DTO)
用於驗證電子郵件變更權杖的輸入。
- `token`: String
- `type`: Enum('OLD_EMAIL', 'NEW_EMAIL')

## 資料庫綱要變更 (PostgreSQL)

```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS display_name VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS address TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500);
ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;

CREATE UNIQUE INDEX IF NOT EXISTS ix_users_phone_number ON users (phone_number) WHERE phone_number IS NOT NULL;
```

## Redis 鍵值 (Keys)

- `email_change:{user_id}:new`: 用於驗證新電子郵件的權杖 (TTL: 24h)
- `email_change:{user_id}:old`: 用於驗證舊電子郵件所有權的權杖 (TTL: 24h)
- `email_change:{user_id}:pending_email`: 儲存待處理的新電子郵件地址 (TTL: 24h)