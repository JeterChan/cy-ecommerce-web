# Data Model: Member System

## Entities

### User

Primary entity representing a registered member.

| Field | Type | Required | Unique | Description |
|-------|------|----------|--------|-------------|
| `id` | UUID | Yes | Yes | Primary Key |
| `username` | String(50) | Yes | Yes | Display name, alphanumeric + underscore/hyphen |
| `email` | String(255) | Yes | Yes | Login credential, valid email format |
| `password_hash` | String(255) | Yes | No | Bcrypt hashed password |
| `is_active` | Boolean | Yes | No | Account status (default True) |
| `created_at` | DateTime | Yes | No | Creation timestamp |
| `updated_at` | DateTime | Yes | No | Last update timestamp |

## Domain Objects (DTOs)

### RegisterInput
- `username`: String (3-50 chars)
- `email`: EmailStr
- `password`: String (Min 8, 1 Upper, 1 Special, 1 Digit)

### LoginInput
- `email`: EmailStr
- `password`: String
- `remember_me`: Boolean

### AuthOutput
- `user`: UserDTO (id, username, email)
- `access_token`: String (JWT)
- `refresh_token`: String (JWT, optional)
