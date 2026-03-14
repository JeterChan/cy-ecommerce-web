# Implementation Plan: Member Cart Async Sync (Celery Implementation)

**Branch**: `019-member-cart-async-sync` | **Date**: 2026-03-13 | **Spec**: [specs/019-member-cart-async-sync/spec.md](spec.md)
**Input**: Feature specification from `/specs/019-member-cart-async-sync/spec.md`

## Summary
實作會員購物車的「寫入快取，非同步同步資料庫」機制。透過 Celery 背景任務與 Redis Stream (Broker) 實現最終一致性。API 層優先更新 Redis 並發送同步任務，由 Celery Worker 負責將變更持久化至 PostgreSQL。

## Technical Context
- **Language/Version**: Python 3.12
- **Primary Dependencies**: FastAPI, Celery, SQLAlchemy, aioredis
- **Storage**: PostgreSQL (Persistence), Redis (Cache & Celery Broker)
- **Testing**: pytest, pytest-celery
- **Performance Goals**: API Latency P95 < 30ms, Sync Latency < 2s
- **Consistency**: Final Consistency (Cache-Aside + Write-Behind)

## Constitution Check
- **高品質 (High Quality)**: 使用 Celery 的自動重試與等冪性設計。
- **可測試性 (Testability)**: 包含非同步任務的集成測試。
- **MVP 優先 (MVP First)**: 專注於核心的同步流程，不引入過度的微服務架構。
- **避免過度設計 (Avoid Overdesign)**: 複用現有的 Celery 基礎設施。
- **正體中文優先 (Traditional Chinese First)**: 文檔與代碼註釋使用正體中文。

## Project Structure

### Documentation (this feature)
```text
specs/019-member-cart-async-sync/
├── plan.md              # 此文件
├── research.md          # Celery vs Redis Stream 決策過程
├── data-model.md        # Redis/Postgres 同步邏輯定義
├── quickstart.md        # Worker 啟動與測試步驟
└── contracts/
    └── cart-sync-task.yaml # Celery Task 定義
```

### Source Code (repository root)
```text
backend/src/
├── core/
│   └── celery.py        # Celery 配置
├── modules/
│   ├── cart/
│   │   ├── application/
│   │   │   └── use_cases/
│   │   │       └── cart_commands.py (發送 Celery 任務)
│   │   ├── infrastructure/
│   │   │   ├── repositories/
│   │   │   │   └── hybrid_repository.py (新：混合儲存邏輯)
│   │   │   └── tasks.py (Celery 任務實作)
│   │   └── presentation/
│   │       └── routes.py (整合混合儲存 Repo)
└── tests/
    └── integration/
        └── test_cart_sync_task.py
```

**Structure Decision**: 採用「混合 Repository (Hybrid Repository)」模式。現有的 `SQLCartRepository` 與 `RedisCartRepository` 將被一個組合類所管理，或在 Use Case 中顯式組合。

## Complexity Tracking
*None*
