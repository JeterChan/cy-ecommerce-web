# cy-ecommerce-web Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-14

## Active Technologies
- Python 3.12 (Constraint) + FastAPI, Redis, PostgreSQL (011-order-module)
- Python 3.12 (Constraint) + FastAPI, Redis, Pydantic (009-cart-merge-system)
- Redis (for Cart data), PostgreSQL (for persistent Member Cart - optional/TBD based on research) (009-cart-merge-system)
- Python 3.12 + FastAPI, Pydantic, SQLAlchemy, Alembic (010-product-module)
- TypeScript 5.x, Vue 3.5 + Axios, Pinia, Vue Router, Tailwind CSS, shadcn/ui (radix-vue) (012-order-frontend-ui)
- N/A (Frontend consumes API; Backend uses PostgreSQL/Redis) (012-order-frontend-ui)
- Python 3.12 (Backend) + FastAPI, SQLAlchemy, Alembic, Celery, Redis, Pydantic (013-user-profile-api)
- PostgreSQL (Users table extension), Redis (Verification Tokens) (013-user-profile-api)
- Python 3.12, TypeScript 5.x, Vue 3.5 + FastAPI, Pydantic v2, SQLAlchemy, Alembic, Boto3 (AWS SDK) (016-product-management-enhancement)
- PostgreSQL (商品與圖片資訊), AWS S3 (圖片檔案) (016-product-management-enhancement)
- Python 3.12, TypeScript 5.x, Vue 3.5 + FastAPI, Vue Router, Pinia, Lucide Icons, shadcn/ui (017-admin-management-portal)
- PostgreSQL (Users table) (017-admin-management-portal)
- Python 3.12 + FastAPI, SQLAlchemy (Async), Redis-py (Async), Pydantic v2 (020-order-checkout-system)
- PostgreSQL (訂單持久化), Redis (購物車暫存) (020-order-checkout-system)

- Python 3.11 (Backend), Node.js/TypeScript (Frontend) (007-member-system)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.11 (Backend), Node.js/TypeScript (Frontend): Follow standard conventions

## Recent Changes
- 020-order-checkout-system: Added Python 3.12 + FastAPI, SQLAlchemy (Async), Redis-py (Async), Pydantic v2
- 017-admin-management-portal: Added Python 3.12, TypeScript 5.x, Vue 3.5 + FastAPI, Vue Router, Pinia, Lucide Icons, shadcn/ui
- 016-product-management-enhancement: Added Python 3.12, TypeScript 5.x, Vue 3.5 + FastAPI, Pydantic v2, SQLAlchemy, Alembic, Boto3 (AWS SDK)


<!-- MANUAL ADDITIONS START -->
- 開發環境不需要執行 `alembic migration`。系統啟動時會自動處理資料表結構同步（透過 `recreate_all`）。
<!-- MANUAL ADDITIONS END -->
