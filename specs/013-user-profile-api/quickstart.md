# 快速開始：使用者個人檔案管理 API

本指南協助您設定並執行使用者個人檔案管理功能。

## 先決條件

- Python 3.12+
- Docker & Docker Compose (用於 PostgreSQL & Redis)
- Git

## 環境設定

1. **複製並安裝依賴**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **啟動基礎設施**
   ```bash
   docker-compose up -d
   ```

3. **執行資料庫遷移**
   ```bash
   alembic upgrade head
   ```

## 執行應用程式

1. **啟動後端伺服器**
   ```bash
   uvicorn src.main:app --reload
   ```

2. **存取 API 文件**
   - 開啟瀏覽器: `http://localhost:8000/docs`
   - 測試 `Auth` / `Users` 標籤下的端點。

## 測試功能

1. **執行測試**
   ```bash
   pytest tests/modules/auth/test_user_profile.py
   ```

2. **手動測試 (使用 cURL 或 Swagger)**

   - **登入**:
     `POST /api/v1/auth/login` -> 取得 `access_token`

   - **取得個人檔案**:
     ```bash
     curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/api/v1/auth/me/profile
     ```

   - **更新個人檔案**:
     ```bash
     curl -X PATCH -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
     -d '{"display_name": "New Name", "bio": "Hello World"}' \
     http://localhost:8000/api/v1/auth/me/profile
     ```

   - **刪除帳戶**:
     ```bash
     curl -X DELETE -H "Authorization: Bearer <TOKEN>" http://localhost:8000/api/v1/auth/me
     ```