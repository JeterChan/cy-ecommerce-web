# Tasks: Product Management Enhancement

**Feature**: Product Management Enhancement
**Status**: Initialized
**Branch**: `016-product-management-enhancement`

## Implementation Strategy
本功能採 MVP 優先策略，先完成後端資料模型與管理員權限基礎，再循序開發各個 User Story。
1. **基礎建設**: 新增 User Role 欄位、S3 整合、ProductImage 資料表。
2. **US1 (P1)**: 管理員 CRUD 介面，優先確保基本增刪改查運作。
3. **US2 (P1)**: 前台庫存顯示與防呆，確保使用者不會買到缺貨商品。
4. **US3 (P2)**: 多圖支援，強化商品展示效果。

## Phase 1: Setup
- [x] T001 [P] 在 `backend/.env.example` 中新增 AWS S3 相關配置項 (BUCKET, ACCESS_KEY, SECRET_KEY)
- [x] T002 [P] 於 `backend/requirements.txt` 新增 `boto3` 依賴
- [x] T003 初始化 S3 基礎設施腳本於 `backend/src/infrastructure/s3.py`

## Phase 2: Foundational
- [x] T004 [P] 更新 `backend/src/modules/auth/domain/entities.py` 中的 `UserEntity` 加入 `role` 欄位
- [x] T005 [P] 更新 `backend/src/modules/auth/infrastructure/models.py` 中的 `UserModel` 加入 `role` 欄位
- [ ] T006 執行 Alembic 遷移以新增 `users.role` 欄位 `backend/alembic/versions/`
- [x] T007 [P] 在 `backend/src/modules/auth/presentation/routes.py` 實作 `require_admin` 依賴項
- [x] T008 [P] 於 `backend/src/modules/product/infrastructure/models.py` 新增 `ProductImageModel` 資料表
- [ ] T009 執行 Alembic 遷移以新增 `product_images` 表 `backend/alembic/versions/`

## Phase 3: User Story 1 - Admin Manages Product Catalog (Priority: P1)
**Goal**: 實作管理員專用的商品 CRUD 介面。
**Independent Test**: 管理員登入後可成功新增、編輯、刪除商品，且變更反映在資料庫。

- [x] T010 [P] [US1] 於 `backend/src/modules/product/presentation/routes.py` 建立管理員專屬的 `/admin/products` 路由
- [x] T011 [US1] 實作 `CreateProductUseCase` 支援管理員權限校驗 `backend/src/modules/product/application/use_cases/create_product.py`
- [x] T012 [P] [US1] 建立前端管理員服務 `frontend/src/services/adminProductService.ts`
- [x] T013 [US1] 實作後台商品列表頁面 `frontend/src/views/admin/ProductManagementView.vue`
- [x] T013a [US1] 實作列表篩選器 (關鍵字、分類、庫存狀態、上架狀態)
- [x] T014 [US1] 實作商品編輯/新增對話框組件 `frontend/src/components/admin/ProductForm.vue`
- [x] T014a [US1] 實作圖片預覽列表、刪除按鈕與主圖 Radio Button 選取 UI
- [x] T015 [US1] 於 `frontend/src/router/index.ts` 新增管理員路由並設定導航守衛

## Phase 4: User Story 2 - Customer Views Real-time Stock Status (Priority: P1)
**Goal**: 前台顯示準確庫存並在缺貨時防呆.
**Independent Test**: 庫存為 0 時，商品卡片顯示「已售罄」且無法加入購物車。

- [x] T016 [P] [US2] 在 `backend/src/modules/product/application/dtos/product_response_dto.py` 使用 `@computed_field` 實作 `is_low_stock`
- [x] T016a [US2] 在 `backend/src/modules/product/infrastructure/repository.py` 實作原子扣減庫存邏輯（使用 SQLAlchemy `with_for_update` 或 `F` 表達式）
- [x] T017 [P] [US2] 於 `frontend/src/components/product/ProductCard.vue` 實作「缺貨/庫存緊張」視覺標籤
- [x] T018 [US2] 更新 `frontend/src/views/ProductDetailView.vue` 加入庫存顯示與「加入購物車」防呆邏輯
- [x] T019 [US2] 在 `frontend/src/components/ui/QuantitySelector.vue` 限制選擇數量不得超過剩餘庫存

## Phase 5: User Story 3 - Multi-Image Product Showcase (Priority: P2)
**Goal**: 支援每個商品最多 5 張圖片與 S3 存儲。
**Independent Test**: 管理員上傳 3 張圖片後，前台商品詳情頁可透過輪播圖查看所有圖片。

- [x] T020 [P] [US3] 在 `backend/src/infrastructure/s3.py` 實作生成 Presigned URL 的邏輯
- [x] T021 [P] [US3] 於 `backend/src/modules/product/presentation/admin_routes.py` 新增 `/admin/products/images/presign` 介面
- [x] T022 [US3] 更新 `backend/src/modules/product/domain/entities.py` 支援 `images` 列表
- [x] T023 [US3] 修改 `frontend/src/components/admin/ProductForm.vue` 支援多圖上傳預覽
- [x] T024 [US3] 在 `frontend/src/views/ProductDetailView.vue` 實作圖片輪播組件 (Carousel)


## Phase 6: Polish & Cross-cutting Concerns
- [x] T025 [P] 統一前後端錯誤處理訊息（如：圖片上傳失敗提示）
- [x] T026 執行完整冒煙測試，確保 Admin 與 User 權限隔離正常
- [x] T027 [US3] 從 `ProductModel` 與 `ProductEntity` 中完全移除 `image_url` 欄位，並更新所有引用該欄位的邏輯

## Dependencies
1. **Phase 2** (Foundational) MUST be completed before **Phase 3** (Admin CRUD).
2. **T020-T021** (S3 logic) MUST be completed before **T023** (Multi-image UI).
3. **US1** (Admin CRUD) 優先於 **US3** (Multi-image)，以確保基本流程穩定。

## Parallel Execution Examples
- **後端開發者**: 可同時進行 T004, T005, T008 (模型定義)。
- **前端開發者**: 可同時進行 T017, T019 (UI 視覺調整)。
- **基礎設施**: 可獨立進行 T001, T002, T003 (S3 設定)。
