# Quickstart: Product Management Enhancement

## 前置準備
1. **AWS S3 設定**: 
    - 建立 S3 Bucket。
    - 取得 `AWS_ACCESS_KEY_ID` 與 `AWS_SECRET_ACCESS_KEY` 並加入 `.env`。
    - 設定 CORS 以允許前端直接上傳。
2. **資料庫遷移**: 
    - 執行 Alembic 生成 `User.role` 與 `ProductImage` 表。
    - `alembic revision --autogenerate -m "add_user_role_and_product_images"`
    - `alembic upgrade head`

## 核心流程

### 1. 管理員權限
- 使用腳本或 DB 介面手動更新帳號角色:
  `UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';`

### 2. 商品建立與圖片上傳
- **Step 1**: 管理員獲取 S3 預簽名 URL: `POST /api/v1/admin/products/images/presign`。
- **Step 2**: 前端使用 `upload_url` 將圖片上傳至 S3。
- **Step 3**: 管理員提交商品資料（包含圖片 URL）: `POST /api/v1/admin/products`。

### 3. 庫存警報
- 前端透過 `GET /api/v1/products/{id}` 獲取商品。
- 檢查 `is_low_stock` 屬性，若為 `true` 則在 UI 顯示「庫存緊張」提示。

## 測試指令
- **後端單元測試**: `pytest backend/tests/unit/modules/product/`
- **整合測試**: `pytest backend/tests/integration/test_product_admin.py`
