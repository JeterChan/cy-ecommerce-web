# 快速開始：商品管理模組 (Product Management Module)

**功能**: 商品管理模組
**日期**: 2026-02-12
**狀態**: 草稿

## 先決條件 (Prerequisites)

1.  **環境**: Python 3.12, Docker, Docker Compose。
2.  **依賴**: `fastapi`, `sqlalchemy`, `pydantic`。

## 設定 (Setup)

1.  **切換分支**:
    ```bash
    git checkout 010-product-module
    ```

2.  **執行遷移**:
    ```bash
    cd backend
    docker-compose exec api alembic upgrade head
    ```

3.  **啟動 API**:
    ```bash
    docker-compose up -d api
    ```

## 測試 (Testing)

1.  **執行單元測試**:
    ```bash
    cd backend
    docker-compose exec api pytest tests/unit/modules/product
    ```

2.  **驗證端點**:
    - 存取 OpenAPI 文件: `http://localhost:8000/docs`
    - 嘗試建立商品:
      - `POST /api/v1/products`
      - Body: `{"name": "測試商品", "price": 100, "stock_quantity": 10}`

## 常見任務 (Common Tasks)

- **新增商品欄位**:
    1. 更新 `backend/src/modules/product/domain/entities.py`。
    2. 更新 `backend/src/modules/product/infrastructure/models.py`。
    3. 產生遷移: `alembic revision --autogenerate -m "add field"`。
    4. 執行遷移。

- **檢查 Log**:
    ```bash
    docker-compose logs -f api
    ```