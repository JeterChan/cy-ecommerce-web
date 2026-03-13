# Quickstart: Member System

## Prerequisites

- Backend running (`docker-compose up api` or local `uvicorn`)
- Frontend running (`npm run dev`)
- Database migrated (`alembic upgrade head`)

## Usage

1.  **Register**:
    - Go to `/register`.
    - Enter Username, Email, Password (e.g., `TestUser1`, `test@example.com`, `Secure@123`).
    - Submit.
    - Result: Auto-login or redirect to Login.

2.  **Login**:
    - Go to `/login`.
    - Enter credentials.
    - Check "Remember Me" (Optional).
    - Result: Redirect to Home, Username shown in Header.

3.  **Logout**:
    - Click Username in Header -> Logout.
    - Result: Redirect to Login/Home, Token cleared.

## Testing

- **Backend**:
  ```bash
  cd backend
  pytest tests/unit/test_register_use_case.py tests/unit/test_login_use_case.py
  ```

- **Frontend**:
  ```bash
  cd frontend
  npm run test:unit
  ```
