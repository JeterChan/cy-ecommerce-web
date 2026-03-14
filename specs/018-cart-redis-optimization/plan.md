# Implementation Plan: Cart Redis Optimization (DDD Alignment)

**Branch**: `018-cart-redis-optimization` | **Date**: 2026-03-13 | **Spec**: [specs/018-cart-redis-optimization/spec.md](spec.md)
**Input**: Feature specification from `/specs/018-cart-redis-optimization/spec.md`

## Summary
實作基於 Redis Hash 的購物車儲存優化，並在現有的 DDD 架構中加入「新增商品時的資料庫鎖定庫存校驗」。僅將 `product_id` 與 `quantity` 儲存在 Redis。檢視購物車時使用現有的 `enrich` 機制動態撈取最新價格。關鍵在於修改 `AddToCartUseCase` 與 `ProductRepository` 以實作 `FOR SHARE` 鎖定校驗。

## Technical Context
- **Language/Version**: Python 3.12 (Constraint from project context)
- **Primary Dependencies**: FastAPI, SQLAlchemy (Async), aioredis, Pydantic v2
- **Storage**: PostgreSQL (Products Truth), Redis (Cart Cache)
- **Testing**: pytest, pytest-asyncio
- **Performance Goals**: SC-001 (Redis < 50ms), SC-004 (Validation < 200ms)
- **Architecture**: Domain-Driven Design (DDD) - Modules: Cart, Product

## Constitution Check
- **高品質 (High Quality)**: 使用 `FOR SHARE` 鎖定而非樂觀鎖，確保跨模組校驗的可靠性。
- **可測試性 (Testability)**: 包含對庫存鎖定併發場景的測試。
- **MVP 優先 (MVP First)**: 重用現有的 `enrich` 機制，專注於解決鎖定與校驗問題。
- **避免過度設計 (Avoid Overdesign)**: 不建立新的模組，而是擴展現有的 Use Case。
- **正體中文優先 (Traditional Chinese First)**: 文檔與註釋使用正體中文。

## Project Structure

### Documentation (this feature)
```text
specs/018-cart-redis-optimization/
├── plan.md              # 此文件
├── research.md          # DDD 整合決策與鎖定策略
├── data-model.md        # Redis/Postgres 實體與過渡
├── quickstart.md        # 實作完成後的驗證步驟
└── contracts/
    └── cart-api.yaml    # API 定義 (現有)
```

### Source Code (repository root)
```text
backend/src/
├── modules/
│   ├── cart/
│   │   ├── application/
│   │   │   └── use_cases/
│   │   │       └── cart_commands.py (修改 AddToCartUseCase)
│   │   ├── domain/
│   │   │   └── repository.py (ICartRepository 定義)
│   │   ├── infrastructure/
│   │   │   └── repositories/
│   │   │       └── redis_repository.py (現有實作)
│   │   └── presentation/
│   │       └── routes.py (依賴注入 ProductRepository)
│   └── product/
│       ├── domain/
│       │   └── repository.py (新增 get_by_id_with_lock 定義)
│       └── infrastructure/
│           └── repository.py (實作 FOR SHARE 鎖定)
└── tests/
    └── integration/
        └── test_cart_redis_optimization.py
```

**Structure Decision**: 遵循現有的 DDD 架構。將 `ProductRepository` 注入 `AddToCartUseCase` 進行業務校驗。

## Complexity Tracking
*None*
