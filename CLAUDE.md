# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack e-commerce application with a Vue 3 frontend and FastAPI backend.

- **Frontend**: Vue 3 + TypeScript + Vite + Pinia + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI + PostgreSQL (async SQLAlchemy) + Redis + Celery
- **Database Migrations**: Alembic

## Development Setup

All backend services run via Docker Compose from the `backend/` directory:

```bash
cd backend
docker compose up --build
```

Services: API (`:8000`), PostgreSQL (`:5432`), Redis (`:6379`), Celery worker/beat, Flower (`:5555`)

Frontend runs standalone:

```bash
cd frontend
npm install
npm run dev   # http://localhost:5173
```

Copy `backend/.env.example` to `backend/.env` before starting.

## Common Commands

### Backend
```bash
cd backend
docker compose up --build                                                              # Start full stack (runs alembic upgrade head automatically)
bash scripts/seed.sh                                                                   # Seed test data (requires running containers)
docker exec ecommerce_api alembic revision --autogenerate -m "描述"                   # Generate new migration after schema changes
pytest                                                                                 # Run all tests
pytest tests/modules/order/                                                            # Run single test module
ruff check .                                                                           # Lint
black .                                                                                # Format
```

### Frontend
```bash
cd frontend
npm run dev          # Dev server
npm run build        # Production build
npm run test:unit    # Vitest unit tests
```

### API Docs
Swagger UI: `http://localhost:8000/api/docs`

## Architecture

### Backend: Clean Architecture per Module

Each module under `backend/src/modules/` follows a four-layer structure:
```
modules/{auth,product,cart,order}/
├── domain/           # Entities, business rules, repository interfaces
├── application/      # Use cases, DTOs
├── infrastructure/   # SQLAlchemy models, repository implementations
└── presentation/     # FastAPI route handlers (routes.py, admin_routes.py)
```

Cross-cutting infrastructure lives in `backend/src/infrastructure/` (database, config, Redis, S3, email, Celery).

**Route prefixes:**
- Auth: `/auth/*`
- Customer APIs: `/api/v1/{products,cart,orders}`
- Admin APIs: `/api/v1/admin/{products,orders}`

### Database

- Async SQLAlchemy with `asyncpg` driver
- `get_db()` dependency auto-commits on success, rolls back on exception
- **Dev & Prod**: `alembic upgrade head` runs automatically at container startup (via `docker-compose.yml` command)
- Schema changes require generating a migration: `docker exec ecommerce_api alembic revision --autogenerate -m "描述"`
- Pessimistic locking (`SELECT ... FOR UPDATE`) used in checkout to prevent race conditions on stock

### Cart System

- **Guest users**: Redis hash storage
- **Authenticated users**: `HybridCartRepository` — writes to Redis, syncs to PostgreSQL via Celery
- Cart syncs from localStorage → backend after login via `authStore.waitForInit()`

### Authentication

- JWT bearer tokens (`access` + `refresh` types)
- Frontend auto-refresh via Axios interceptor in `frontend/src/lib/api.ts`
- Route guards in `frontend/src/router/index.ts` use `requiresAuth` and `requiresAdmin` meta flags

### Frontend State Management

- Pinia stores in `frontend/src/stores/`
- API calls isolated in `frontend/src/services/`
- `authStore.initAuth()` runs on app mount; all guarded routes wait for `waitForInit()` to resolve

### Celery Queues

- `email_queue` — transactional emails via Brevo
- `cart_sync_queue` — Redis → PostgreSQL cart sync
- `default` — cleanup and misc tasks
- Beat schedule: account cleanup every 24h
