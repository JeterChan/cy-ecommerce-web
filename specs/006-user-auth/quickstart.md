# 快速入門: 使用者驗證開發

## 環境設置

1. **切換到後端目錄**
   ```bash
   cd backend
   ```

2. **安裝新依賴**
   ```bash
   # 新增到 requirements.txt (如果尚未存在)
   # fastapi, uvicorn, sqlalchemy, asyncpg, alembic, passlib[bcrypt], python-jose[cryptography], pydantic-settings
   pip install -r requirements.txt
   ```

3. **啟動資料庫**
   ```bash
   docker-compose up -d db
   ```

## 資料庫遷移 (Alembic)

1. **初始化 Alembic (如果尚未初始化)**
   ```bash
   # 只需執行一次
   alembic init alembic
   ```

2. **產生遷移腳本**
   ```bash
   # 在定義好 User model 後
   alembic revision --autogenerate -m "Add user table"
   ```

3. **執行遷移**
   ```bash
   alembic upgrade head
   ```

## 測試 API

1. **啟動開發伺服器**
   ```bash
   uvicorn src.main:app --reload
   ```

2. **存取 Swagger UI**
   - 打開瀏覽器: `http://localhost:8000/docs`
   - 使用 `/api/v1/auth/register` 註冊新使用者
   - 使用 `/api/v1/auth/login` 登入 (記得點選右上角 Authorize 按鈕)
   - 測試 `/api/v1/users/me`

## 常見指令

- **執行測試**:
  ```bash
  pytest tests/
  ```
