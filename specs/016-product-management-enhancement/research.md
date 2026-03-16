# Research: Product Management Enhancement

## Decisions

### 1. 管理員權限區分 (Admin Authentication)
- **Decision**: 在 `User` 資料表中新增 `role` 欄位（Enum），預設為 `user`，手動或透過腳本設定特定帳號為 `admin`。
- **Rationale**: 現有的 `UserEntity` 缺乏角色區分，新增 `role` 欄位是最簡單且符合未來擴充（如 `staff`, `editor`）的做法。
- **Alternatives considered**: 
    - 使用 `is_admin` 布林值（擴充性較差）。
    - 建立獨立的 `Admin` 資料表（過度設計，且與現有認證邏輯衝突）。

### 2. 多圖儲存方案 (Multi-image Storage)
- **Decision**: 使用 AWS S3 儲存圖片，後端提供 Presigned URL 供前端直接上傳或存取。
- **Rationale**: S3 是處理靜態資源的標準做法。使用 Presigned URL 可以減輕後端伺服器傳輸大檔案的負擔。
- **Alternatives considered**: 
    - 儲存在本地伺服器（擴展性差，備份困難）。
    - 將圖片轉為 Base64 存入資料庫（資料庫膨脹，效能極差）。

### 3. 即時庫存預警 (Real-time Stock Alert)
- **Decision**: 使用 Pydantic v2 的 `@computed_field` 在 DTO 層級進行計算。
- **Rationale**: 符合使用者「即時計算」的要求，且不會增加資料庫存儲冗餘數據。邏輯集中在展示層。
- **Alternatives considered**: 
    - 前端計算（邏輯分散，不易統一維護）。
    - 資料庫觸發器/存儲欄位（增加寫入複雜度）。

### 4. API 保護機制 (API Protection)
- **Decision**: 建立一個 FastAPI Dependency `require_admin`。
- **Rationale**: 簡潔且易於在多個路由中重複使用，符合 FastAPI 的慣用法。

## Research Tasks

- [x] 確認 `User` 實體是否需要 Role 欄位 -> 需要新增。
- [x] 研究 Pydantic v2 `@computed_field` 用法。
- [x] 研究 Boto3 生成 S3 Presigned URL 的範例。
- [x] 確認現有資料庫 Migration 工具（Alembic）的使用方式。

### 5. S3 檔案限制與一致性 (Consistency)
- **限制**: 支援 JPEG, PNG, WEBP，上限 5MB。
- **一致性**: 採用 S3 生命週期規則自動清理未引用的 /temp 檔案。若資料庫寫入失敗，檔案將在 24 小時後被 S3 自動移除。

### 6. 商品生命週期 (Deactivate vs Soft Delete)
- **下架**: 變更 `is_active`。適用於營運調整。
- **軟刪除**: 變更 `deleted_at`。適用於永久下架，保留歷史資料。

### 7. 後台管理 UI 規格
- **篩選器**: 需包含關鍵字、分類、庫存警示、上下架狀態。
- **多圖管理**: 提供縮圖預覽、刪除、及單選標記主圖功能。
