# 快速入門: 購物車合併系統

## 前置需求

- **Python 3.12+**
- **Docker** (用於 Redis/Postgres)

## 設定

1. **啟動基礎設施**:
   ```bash
   cd backend
   docker-compose up -d redis db
   ```

2. **安裝依賴**:
   ```bash
   pip install -r backend/requirements.txt
   ```

## 執行應用程式

1. **啟動後端**:
   ```bash
   cd backend/src
   uvicorn main:app --reload
   ```

## 測試 API

### 1. 訪客流程
```bash
# 以訪客身分加入商品 (無 auth header)
curl -X POST http://localhost:8000/api/v1/cart/items \
  -H "Content-Type: application/json" \
  -d '{"product_id": "uuid...", "quantity": 1}' \
  -c cookies.txt
```

### 2. 登入與合併
```bash
# 登入 (模擬) - 這應該在內部觸發合併
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "password"}' \
  -b cookies.txt
```

### 3. 驗證合併
```bash
# 取得購物車 (已驗證)
curl -X GET http://localhost:8000/api/v1/cart \
  -H "Authorization: Bearer <token>"
```