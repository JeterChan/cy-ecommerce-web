# 研究報告：商品管理模組 (Product Management Module)

**功能**: 商品管理模組
**日期**: 2026-02-12
**狀態**: 完成

## 1. 架構模式 (Architectural Pattern)
**決策**: Clean Architecture (分層式)
**理由**:
- 使用者明確要求（「採用與現在專案相同的 Clean architecture」）。
- 與現有的 `auth` 模組結構一致。
- 分離關注點：Domain（商業規則）與 Infrastructure（資料庫/API）。

**結構**:
- `domain/`: 實體、Repository 介面、Pydantic Schemas。
- `use_cases/`: 商業邏輯互動器（例如 `CreateProductUseCase`）。
- `infrastructure/`: SQLAlchemy 模型、Repository 實作。
- `api/`: FastAPI 路由（控制器）。

## 2. 資料庫技術 (Database Technology)
**決策**: PostgreSQL + SQLAlchemy (Async)
**理由**:
- 專案標準（基於 `backend/src/modules/auth/infrastructure/models`）。
- 關聯式資料（Products <-> Categories）適合 SQL。
- 高併發需要 Async 支援。

## 3. 商品與分類關係 (Product & Category Relationship)
**決策**: 多對多 (Many-to-Many)
**分析**:
- 規格書提到 "Product ... category_id: Reference to Category"。
- 規格書也提到 "assign a product to one or more categories" (FR-004)。
- **改良**: 為了滿足 FR-004，我們需要多對多關係（或簡化的的一對多，如果偏好嚴格的「主分類」，但 FR-004 暗示多個）。
- **結論**: 我們將使用關聯表 `product_category_association` 實作多對多關係。

## 4. 圖片處理 (Image Handling)
**決策**: 儲存圖片 URL (字串)
**理由**:
- 規格書要求 `image_url`。
- 實際檔案上傳處理（S3、本地磁碟）不在此特定規格範圍內，除非特別指定，但規格書說「提供有效的圖片 URL 或上傳圖片」。
- **簡化**: 對於此 MVP 模組，我們將儲存字串 URL。「上傳」端點可以在儲存到靜態資料夾後僅回傳 URL，或暫時模擬，因為尚未定義儲存後端。我們將假設 API 接受 URL 或在單獨的 `upload` 端點處理檔案上傳並回傳 URL。

## 5. Python 版本
**決策**: Python 3.12
**理由**: 使用者限制。