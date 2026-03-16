# 實作任務：使用者個人檔案管理 API

**功能**: `013-user-profile-api`

## 實作策略

我們將逐步建立使用者個人檔案管理 API，從核心資料庫更新開始，接著是基礎服務 (Redis、電子郵件)。然後，我們將依優先順序個別實作每個使用者故事，從檢視個人檔案 (MVP)、更新個人檔案 (包括複雜的電子郵件變更流程)，最後是帳戶刪除流程。

## 依賴關係與執行順序

1.  **階段 1 和 2 (設定與基礎)** 必須先完成，以建立資料庫綱要、Redis 權杖管理和電子郵件基礎設施。
2.  **階段 3 (使用者故事 1 - 檢視個人檔案)** 是獨立的，構成 MVP。
3.  **階段 4 (使用者故事 2 - 更新個人檔案)** 需要階段 1 和 2，但可以獨立於階段 3 進行開發。
4.  **階段 5 (使用者故事 3 - 刪除帳戶)** 需要階段 1，並且可以與階段 4 並行執行。

## 階段 1：設定
*目標：更新底層資料庫綱要和領域實體以支援個人檔案欄位。*

- [x] T001 更新 `UserEntity` 以包含新的個人檔案欄位 (`display_name`、`phone_number`、`address`、`avatar_url`、`bio`、`deleted_at`) 於 `backend/src/modules/auth/domain/entity.py`
- [x] T002 更新 SQLAlchemy User 模型以包含新欄位於 `backend/src/infrastructure/models.py`
- [x] T003 為使用者個人檔案欄位產生 Alembic 遷移腳本於 `backend/`

## 階段 2：基礎
*目標：實作電子郵件驗證流程所需的基礎服務。*

- [x] T004 實作 Redis 權杖管理器，用於電子郵件驗證權杖於 `backend/src/modules/auth/infrastructure/redis_token_manager.py`
- [x] T005 建立 EmailService 介面和實作，用於發送驗證電子郵件於 `backend/src/infrastructure/email_service.py`

## 階段 3：使用者故事 1 - 檢視個人檔案
*目標：允許已驗證的使用者檢索其個人檔案資訊。*
*獨立測試：驗證使用者並呼叫 `GET /api/v1/auth/me/profile`，驗證回應是否符合 DTO。*

- [x] T006 [P] [US1] 在 `backend/src/modules/auth/application/dtos.py` 中新增 `UserProfileResponse` DTO
- [x] T007 [US1] 實作 `GetProfileUseCase` 以獲取使用者資料於 `backend/src/modules/auth/application/use_cases/get_profile.py`
- [x] T008 [US1] 在 `backend/src/modules/auth/presentation/routes.py` 中新增 `GET /api/v1/auth/me/profile` 端點，對應到 Use Case
- [x] T009 [US1] 撰寫檢視個人檔案 API 的整合測試於 `backend/tests/modules/auth/test_user_profile.py`

## 階段 4：使用者故事 2 - 更新個人檔案與電子郵件
*目標：允許已驗證的使用者更新其個人檔案詳細資料並安全地更改其電子郵件地址。*
*獨立測試：透過 `PATCH` 更新基本欄位，然後啟動電子郵件變更，驗證權杖，並確認電子郵件已更新。*

- [x] T010 [P] [US2] 在 `backend/src/modules/auth/application/dtos.py` 中新增 `UpdateProfileRequest`、`EmailChangeRequest`、`VerifyEmailChangeRequest` DTO
- [x] T011 [US2] 實作 `UpdateProfileUseCase` 以更新基本個人檔案欄位於 `backend/src/modules/auth/application/use_cases/update_profile.py`
- [x] T012 [P] [US2] 建立 Celery 任務以非同步發送電子郵件於 `backend/src/infrastructure/tasks/email_tasks.py`
- [x] T013 [US2] 實作 `RequestEmailChangeUseCase` 以生成權杖並觸發電子郵件於 `backend/src/modules/auth/application/use_cases/request_email_change.py`
- [x] T014 [US2] 實作 `VerifyEmailChangeUseCase` 以驗證權杖並更新電子郵件於 `backend/src/modules/auth/application/use_cases/verify_email_change.py`
- [x] T015 [US2] 在 `backend/src/modules/auth/presentation/routes.py` 中新增 `PATCH /api/v1/auth/me/profile` 端點
- [x] T016 [US2] 在 `backend/src/modules/auth/presentation/routes.py` 中新增 `POST /api/v1/auth/me/email/change` 端點
- [x] T017 [US2] 在 `backend/src/modules/auth/presentation/routes.py` 中新增 `GET /api/v1/auth/me/email/verify` 端點
- [x] T018 [US2] 撰寫個人檔案更新和電子郵件變更流程的測試於 `backend/tests/modules/auth/test_user_profile.py`

## 階段 5：使用者故事 3 - 刪除帳戶
*目標：允許使用者安全地刪除其帳戶，採用軟刪除後延遲硬刪除的方式。*
*獨立測試：呼叫 `DELETE /api/v1/auth/me`，驗證帳戶已停用且使用者無法登入。驗證硬刪除 Celery 任務對舊帳戶有效。*

- [x] T019 [P] [US3] 實作 `DeleteAccountUseCase` 以進行軟刪除和權杖失效於 `backend/src/modules/auth/application/use_cases/delete_account.py`
- [x] T020 [US3] 在 `backend/src/modules/auth/presentation/routes.py` 中新增 `DELETE /api/v1/auth/me` 端點
- [x] T021 [P] [US3] 建立每日 Celery Beat 任務以對過期帳戶進行硬刪除於 `backend/src/infrastructure/tasks/cleanup_tasks.py`
- [x] T022 [US3] 撰寫帳戶刪除的整合測試於 `backend/tests/modules/auth/test_user_profile.py`

## 階段 6：完善
*目標：最終審查跨領域考量。*

- [x] T023 確保所有 API 端點正確地將領域例外映射到標準 HTTP 錯誤回應，並在需要時更新 OpenAPI 規格。