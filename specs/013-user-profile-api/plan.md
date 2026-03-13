# 實作計畫：使用者個人檔案管理 API

**分支**: `013-user-profile-api` | **日期**: 2026-02-23 | **規格**: [spec.md](./spec.md)
**輸入**: 來自 `specs/013-user-profile-api/spec.md` 的功能規格

## 摘要

在 Auth 模組中實作使用者個人檔案管理 API。包含檢視與更新個人檔案詳細資料（顯示名稱、電話、地址、簡介、頭像）、具備雙重驗證的安全電子郵件變更，以及延遲帳戶刪除（軟刪除 + 30 天硬刪除）。

## 技術上下文

**語言/版本**: Python 3.12 (後端)
**主要依賴**: FastAPI, SQLAlchemy, Alembic, Celery, Redis, Pydantic
**儲存**: PostgreSQL (Users 資料表擴充), Redis (驗證權杖)
**測試**: pytest
**目標平台**: Linux (Docker 容器)
**專案類型**: Web 後端 (模組化單體架構)
**效能目標**: API 回應時間 < 200ms (p95)
**限制**: 乾淨架構 (Clean Architecture), RESTful API
**規模/範圍**: 約 5 個新端點, 1 個新的背景任務

## 憲法檢查

*閘門：必須在階段 0 研究之前通過。在階段 1 設計後重新檢查。*

- [x] **高品質**: 遵循 Clean Architecture 與現有模式。
- [x] **可測試性**: 邏輯隔離在 Use Cases 中，可透過單元/整合測試進行測試。
- [x] **MVP 優先**: 僅包含核心個人檔案欄位和必要流程（電子郵件變更、刪除）。
- [x] **避免過度設計**: 重複使用現有的 Auth 模組，而非建立新的微服務。
- [x] **正體中文優先**: 所有文件與註解皆使用正體中文。

## 專案結構

### 文件 (此功能)

```text
specs/013-user-profile-api/
├── plan.md              # 此檔案
├── research.md          # 技術決策 (電子郵件流程、刪除策略)
├── data-model.md        # 資料庫綱要變更與 DTOs
├── quickstart.md        # 如何執行與測試
├── contracts/           # OpenAPI 規格
│   └── openapi.yaml
└── tasks.md             # 產生的任務
```

### 原始碼 (儲存庫根目錄)

```text
backend/
├── src/
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── presentation/
│   │   │   │   └── routes.py          # 新增新端點
│   │   │   ├── application/
│   │   │   │   ├── use_cases/         # 新增個人檔案 Use Cases
│   │   │   │   │   ├── get_profile.py
│   │   │   │   │   ├── update_profile.py
│   │   │   │   │   ├── request_email_change.py
│   │   │   │   │   ├── verify_email_change.py
│   │   │   │   │   └── delete_account.py
│   │   │   │   └── dtos.py            # 新增個人檔案 DTOs
│   │   │   ├── domain/
│   │   │   │   └── entity.py          # 更新 UserEntity
│   │   │   └── infrastructure/
│   │   │       ├── repositories/      # 更新 UserRepository
│   │   │       └── tasks/             # Celery 任務 (刪除、電子郵件)
│   └── main.py
└── tests/
    └── modules/
        └── auth/
            └── test_user_profile.py
```

**結構決策**: 在模組化單體架構 (Modular Monolith architecture) 中擴充現有的 `auth` 模組。

## 複雜度追蹤

| 違規 | 為何需要 | 拒絕更簡單替代方案的原因 |
|-----------|------------|-------------------------------------|
| 無      | N/A        | N/A                                 |
