## Context

目前後端採用 Clean Architecture，每個模組分為 domain、application、infrastructure、presentation 四層。現有測試以整合測試為主（需連線 PostgreSQL + Redis），僅 auth 模組有部分 use case 單元測試。Domain 層（entities、value objects）和 application 層（use cases）的純邏輯幾乎沒有單元測試覆蓋。

現有測試目錄結構：
- `tests/shared/` — 共用 domain primitives 的純單元測試（已完備）
- `tests/unit/modules/auth/` — auth use case 單元測試（部分覆蓋）
- `tests/unit/` 根目錄 — 舊版 auth 測試（import 路徑過時，無法執行）
- `tests/modules/order/` — order 整合測試
- `tests/integration/` — 跨模組整合測試

## Goals / Non-Goals

**Goals:**
- 為 product、cart、order 三個模組的 domain entity 和 use case 建立單元測試
- 為 `StockRedisService` 建立完整單元測試
- 補強 auth 模組的 `DeleteAccountUseCase` 和 `UpdateProfileUseCase` 測試
- 所有單元測試使用 mock 隔離外部依賴（DB、Redis），可離線快速執行
- 測試檔案結構與現有 `tests/unit/modules/auth/` 保持一致

**Non-Goals:**
- 不重寫或修復 `tests/unit/` 根目錄下的舊版測試（那些是遺留代碼）
- 不新增整合測試（現有整合測試已足夠）
- 不修改任何正式程式碼
- 不測試 presentation 層（route handler），那屬於整合測試範疇
- 不測試 infrastructure 層的 repository 實作（需要真實 DB）

## Decisions

### 1. 測試目錄結構

按模組分目錄，與 src 結構對應：

```
tests/unit/
├── modules/
│   ├── auth/          # 既有，補強
│   ├── product/       # 新增
│   │   ├── test_entities.py
│   │   └── test_use_cases.py
│   ├── cart/
│   │   ├── test_use_cases.py
│   │   └── test_merge_service.py
│   └── order/
│       ├── test_entities.py
│       └── test_use_cases.py
└── infrastructure/
    └── test_stock_redis_service.py
```

**理由：** 與現有 `tests/unit/modules/auth/` 風格一致，且按模組分類方便定位。

### 2. Mock 策略

- 使用 `unittest.mock.AsyncMock` mock 所有 repository 介面（`IUserRepository`、`IProductRepository` 等）
- 使用 `unittest.mock.MagicMock` / `AsyncMock` mock Redis client
- 使用 `AsyncMock` mock `IPasswordHasher`、`IEmailService` 等 domain service
- `StockRedisService` 測試使用 mock Redis client（`AsyncMock`）而非真實 Redis

**理由：** 與現有 `tests/unit/modules/auth/test_use_cases.py` 的做法一致，也是 Clean Architecture 的標準做法——測試 domain/application 層時不應依賴 infrastructure。

### 3. Domain entity 測試為純函式測試

Domain entity（`Product`、`Order`、`OrderItem`、`Category`）的 `validate()` 方法是純函式邏輯，不需要任何 mock，直接建構 entity 並呼叫 validate。

### 4. 在新 branch 上開發

所有測試程式碼在獨立 branch（如 `feat/add-backend-unit-tests`）上開發，完成後再合併。

## Risks / Trade-offs

- **Mock 與實際行為偏離** → 現有整合測試覆蓋了端到端流程，單元測試專注於分支邏輯和邊界條件，兩者互補
- **舊版測試未清理** → 非本次範圍，但不會造成衝突（不同目錄），未來可另行清理
- **StockRedisService mock 測試無法驗證 Redis 原子性** → 已有整合測試（`test_checkout_concurrency.py`）驗證併發場景，單元測試專注驗證分支邏輯（lazy-init、rollback 路徑）
