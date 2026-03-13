# 任務列表：商品管理模組 (Product Management Module)

**功能**: 商品管理模組
**分支**: `010-product-module`
**狀態**: 待處理
**進度**: 0/26

## 實作策略 (Implementation Strategy)
- **方法**: 遵循 Clean Architecture 的增量實作。
- **階段**:
    1.  **設定 (Setup)**: 初始化目錄結構。
    2.  **基礎 (Foundation)**: 定義 Domain 實體、SQLAlchemy 模型和 Repositories。
    3.  **US1 (商品)**: 實作商品的 CRUD。
    4.  **US2 (分類)**: 實作分類的 CRUD 和商品-分類關聯。
    5.  **US3 (圖片)**: 驗證圖片 URL 處理。
- **測試**: Use Cases 的單元測試，API 端點的整合測試。

## 依賴關係 (Dependencies)
- **階段 1 & 2** 是所有 User Stories 的先決條件。
- **US2** 擴充了 US1（增加了分類關係），因此 US1 應先穩定（雖然如果小心合併，它們可以並行開發）。
- **US3** 是對 US1 的小幅增強。

## 平行執行機會 (Parallel Execution Opportunities)
- **US1 內部**: 一旦 Entities/Repositories 準備就緒，Use Cases (T008-T011) 可以平行實作。
- **US1 & US2**: 分類 CRUD (US2) 可以與商品 CRUD (US1) 一起實作，稍後再合併關聯邏輯。

---

## 階段 1：設定 (Phase 1: Setup)

*目標：初始化模組結構。*

- [ ] T001 建立模組目錄結構 `backend/src/modules/product`，包含子目錄 `api/v1`, `domain`, `infrastructure/repositories`, `use_cases`。

## 階段 2：基礎 (Phase 2: Foundational) - 阻礙性先決條件

*目標：定義所有故事所需的資料層（實體、模型、遷移）。*
*獨立測試：透過 Alembic 成功建立資料庫表格。*

- [ ] T002 在 `backend/src/modules/product/domain/entities.py` 中定義 Domain 實體 (`Product`, `Category`)。
- [ ] T003 在 `backend/src/modules/product/domain/repository.py` 中定義 Repository 介面。
- [ ] T004 在 `backend/src/modules/product/infrastructure/models.py` 中定義 SQLAlchemy 模型 (`ProductModel`, `CategoryModel`, `association_table`)。
- [ ] T005 在 `backend/alembic/versions/` 中產生 Alembic 遷移腳本。
- [ ] T006 在 `backend/src/modules/product/infrastructure/repositories.py` 中實作 `SqlAlchemyProductRepository` 和 `SqlAlchemyCategoryRepository`。

## 階段 3：User Story 1 - 管理商品 (優先級 P1)

*目標：允許管理員建立、讀取、更新和刪除商品。*
*獨立測試：透過 API 建立商品並檢索它。*

- [ ] T007 [US1] 在 `backend/src/modules/product/domain/schemas.py` 中定義 Pydantic Schemas (`ProductCreate`, `ProductUpdate`, `ProductResponse`)。
- [ ] T008 [P] [US1] 在 `backend/src/modules/product/use_cases/create_product.py` 中實作 `CreateProductUseCase`。
- [ ] T009 [P] [US1] 在 `backend/src/modules/product/use_cases/get_product.py` 中實作 `GetProductUseCase` 和 `GetProductListUseCase`。
- [ ] T010 [P] [US1] 在 `backend/src/modules/product/use_cases/update_product.py` 中實作 `UpdateProductUseCase`。
- [ ] T011 [P] [US1] 在 `backend/src/modules/product/use_cases/delete_product.py` 中實作 `DeleteProductUseCase`。
- [ ] T012 [US1] 在 `backend/src/modules/product/api/v1/products.py` 中實作 Product API Router。
- [ ] T013 [US1] 在 `backend/src/main.py` (或模組 init) 中註冊 Product router。
- [ ] T014 [US1] 在 `backend/tests/unit/modules/product/test_product_use_cases.py` 中新增 Product Use Cases 的單元測試。
- [ ] T015 [US1] 在 `backend/tests/integration/modules/product/test_product_api.py` 中新增 Product API 的整合測試。

## 階段 4：User Story 2 - 管理分類 (優先級 P2)

*目標：允許管理員管理分類並將其指派給商品。*
*獨立測試：建立分類，將其指派給商品，並依分類篩選商品。*

- [ ] T016 [US2] 在 `backend/src/modules/product/domain/schemas.py` 中定義 Pydantic Schemas (`CategoryCreate`, `CategoryUpdate`, `CategoryResponse`)。
- [ ] T017 [US2] 在 `backend/src/modules/product/use_cases/category_use_cases.py` 中實作 Category CRUD Use Cases。
- [ ] T018 [US2] 在 `backend/src/modules/product/api/v1/categories.py` 中實作 Category API Router。
- [ ] T019 [US2] 更新 `CreateProductUseCase` 和 `UpdateProductUseCase` 以處理 `category_ids` 指派。
- [ ] T020 [US2] 更新 `SqlAlchemyProductRepository` 以處理多對多關聯的持久化。
- [ ] T021 [US2] 在 `backend/src/main.py` 中註冊 Category router。
- [ ] T022 [US2] 在 `backend/tests/integration/modules/product/test_categories.py` 中新增分類的單元/整合測試。

## 階段 5：User Story 3 - 商品圖片管理 (優先級 P3)

*目標：允許將圖片 URL 與商品關聯。*
*獨立測試：儲存帶有圖片 URL 的商品並驗證其持久化。*

- [ ] T023 [US3] 驗證 `image_url` 在 `ProductCreate` 和 `ProductUpdate` schemas 及 models 中被正確處理（檢閱/更新 `backend/src/modules/product/domain/schemas.py` 和 `models.py`）。
- [ ] T024 [US3] 在 `backend/tests/integration/modules/product/test_product_api.py` 中新增驗證與持久化 `image_url` 的測試案例。

## 階段 6：潤飾與跨切面關注點 (Phase 6: Polish & Cross-Cutting)

- [ ] T025 執行 `ruff check .` 並修復 `backend/src/modules/product` 中的任何 linting 錯誤。
- [ ] T026 使用 `pytest backend/tests/` 驗證所有測試皆通過。