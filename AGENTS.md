# AGENTS.md

## Project Snapshot
- This repo is a frontend/backend e-commerce app with a **modular monolith** backend (`backend/src/modules/{auth,product,cart,order}`) and a Vue 3 frontend (`frontend/src`).
- Backend is FastAPI + async SQLAlchemy + Redis + Celery; frontend is Vue 3 + Pinia + Vue Router + Axios.
- API docs are served at `/api/docs` (`backend/src/main.py`), with most business routes mounted under `/api/v1`.

## Architecture You Should Learn First
- Backend layering is consistent per module: `domain` -> `application` (use cases/DTOs) -> `infrastructure` (repos/models) -> `presentation` (FastAPI routes).
- Routes usually construct repositories/use-cases inline (example: `modules/product/presentation/routes.py`) instead of using a separate DI container.
- `get_db()` commits automatically after route execution and rolls back on exception (`backend/src/infrastructure/database.py`); avoid double-commit patterns in route handlers.
- DB tables are auto-created at startup via `init_db()` in app lifespan (`backend/src/main.py`); docs note dev flow does not rely on Alembic migration runs (`GEMINI.md`).
- `backend/src/infrastructure/models.py` centralizes model imports so `Base.metadata.create_all()` sees module tables.

## Critical Cross-Module Flows
- Auth is JWT bearer with token type checks (`backend/src/core/security.py`), current-user resolution in `modules/auth/presentation/routes.py`, and frontend auto-refresh in `frontend/src/lib/api.ts`.
- Cart has guest/member split:
  - Guest: Redis hash storage (`modules/cart/infrastructure/repositories/redis_repository.py`).
  - Member: `HybridCartRepository` write-behind to Redis + async sync to Postgres via Celery (`modules/cart/infrastructure/repositories/hybrid_repository.py`).
- Cart sync task uses Redis distributed lock and Postgres UPSERT semantics (`modules/cart/infrastructure/tasks.py`).
- Checkout is atomic and stock-safe: locks products with `FOR UPDATE`, decrements stock, creates order, then clears cart (`modules/order/application/use_cases/checkout.py`).
- Order cancellation restocks only when transitioning from `PENDING` to `CANCELLED` (`modules/order/application/use_cases/update_order_status.py`).

## Frontend Integration Patterns
- API calls live in `frontend/src/services/*`; stores orchestrate UI state + backend sync (`frontend/src/stores/auth.ts`, `frontend/src/stores/cart.ts`).
- Router guards depend on `authStore.waitForInit()` and enforce `requiresAuth` / `requiresAdmin` (`frontend/src/router/index.ts`).
- Token-expiry handling is centralized: Axios interceptor clears storage and triggers callback set in `frontend/src/main.ts`.
- Cart store uses localStorage as fallback and then syncs from backend after auth init; preserve this behavior when editing cart UX.

## Developer Workflows (Observed)
- Full stack via Docker Compose from `backend/`: `docker-compose up --build` (`README.md`, `backend/docker-compose.yml`).
- Frontend local scripts (`frontend/package.json`): `npm run dev`, `npm run build`, `npm run test:unit`.
- Backend tests run with pytest config in `backend/pytest.ini`; tests are under `backend/tests/{unit,integration,...}`.
- Test bootstrap loads `.env.test` and patches specific env parsing issues (`backend/tests/conftest.py`); keep this in mind before changing env parsing behavior.
- Seed helpers exist in `backend/scripts/` (for example `python -m scripts.seed_categories`, `python -m scripts.seed_admin`).

## External Integrations and Queues
- Redis is used for both cache/cart and token workflows (`infrastructure/database.py`, `infrastructure/redis/token_manager.py`).
- Celery queues include `email_queue` and `cart_sync_queue` (`backend/src/infrastructure/celery_app.py`); cart sync depends on workers consuming `cart_sync_queue`.
- S3 presigned upload URL generation is optional and credential-gated (`backend/src/infrastructure/s3.py`, admin product routes).

## Spec Artifacts
- `specs/` contains numbered feature specs and quickstarts that reflect implemented behavior (for example `specs/020-order-checkout-system/quickstart.md`).
- Use specs as behavior references when code intent is unclear, but trust runtime code paths first.
