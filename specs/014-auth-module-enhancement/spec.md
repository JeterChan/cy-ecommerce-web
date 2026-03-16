# Feature Specification: Auth Module Enhancement

**Feature Branch**: `014-auth-module-enhancement`  
**Created**: 2026-03-10  
**Status**: Draft  
**Input**: User description: "新增 Auth Module 功能，根據 @specs/014-auth-module-enhancement/spec.md 描述的 User story 建立其餘的文件"

## 1. Overview
### 1.1 Problem Statement
目前系統已經有基本的 `auth` 模組，提供註冊、登入、刷新 Token 以及個人檔案讀取與更新功能。然而，為了提供更完整且安全的會員體驗，我們需要擴充現有的會員模組。具體來說，需要增加註冊時的電子郵件確認機制以驗證使用者身分，提供忘記密碼功能以協助使用者找回帳號，允許在個人檔案頁面修改密碼與使用者名稱，並讓使用者能夠自主刪除帳號以及更新更多基本資訊。

### 1.2 Target Audience
- **一般使用者/會員**：需要更安全可靠的帳號管理機制，以及更完整的個人資料控制權。
- **系統管理員/客服**：減少處理使用者忘記密碼或修改基本資料的支援請求。

### 1.3 Value Proposition
- 提升帳號安全性（信箱驗證、密碼修改、忘記密碼）。
- 增強使用者對個人資料控制權（刪除帳號、修改基本資訊、更改使用者名稱）。
- 完善現有的 `auth` 模組，使其符合業界標準的會員系統。

## 2. User Scenarios & Testing

### User Story 1 - 註冊與信箱驗證 (Priority: P1)

作為一名新使用者，我希望在註冊後能夠收到驗證信件並驗證我的 Email，以確保我的帳號安全且信箱真實有效。

**Why this priority**: 核心安全功能，防止垃圾帳號註冊，並為後續密碼重設提供可信媒介。

**Independent Test**: 可以獨立於密碼重設等功能進行測試。只需實作註冊端點與驗證連結端點，即可達成驗證信箱的 MVP。

**Acceptance Scenarios**:

1. **Given** 使用者輸入註冊資訊，**When** 提交註冊，**Then** 系統建立 `is_verified=False` 且 `is_active=True` 的帳號，並發送包含 Token 的驗證連結至使用者信箱。
2. **Given** 使用者點擊信件中的驗證連結，**When** Token 有效且未過期，**Then** 系統將帳號狀態更新為 `is_verified=True`，使用者可正常登入。
3. **Given** 使用者嘗試登入未驗證的帳號，**When** 帳號狀態為 `is_verified=False`，**Then** 系統提示「請先完成信箱驗證」。

---

### User Story 2 - 忘記密碼與重設流程 (Priority: P1)

作為一名忘記密碼的使用者，我希望可以透過我的註冊信箱重設密碼，以便我能重新取得帳號存取權。

**Why this priority**: 提升使用者滿意度並大幅降低客服成本，是會員系統的必備功能。

**Independent Test**: 只需實作請求重設端點與執行重設端點，即可透過 Postman 或自動化測試驗證流程。

**Acceptance Scenarios**:

1. **Given** 使用者在登入頁點擊忘記密碼並輸入 Email，**When** 提交請求，**Then** 系統發送包含 Reset Token 的連結至該信箱。
2. **Given** 使用者輸入一個未註冊的 Email，**When** 提交請求，**Then** 系統回應「若信箱存在，將發送重設信件」，不應洩漏 Email 是否已註冊。
3. **Given** 使用者點擊重設連結並輸入新密碼，**When** Token 有效且新舊密碼符合格式規範，**Then** 系統更新密碼雜湊值並使 Token 失效。

---

### User Story 3 - Profile 頁面變更資訊 (Priority: P2)

作為一名登入的使用者，我希望能在 Profile 頁面變更我的密碼、使用者名稱與基本資訊，以保持我的個人資料是最新的且安全的。

**Why this priority**: 使用者體驗的核心需求，提升對帳號資料的控制權。

**Independent Test**: 可以分項實作（先密碼，後使用者名稱與基本資訊）。

**Acceptance Scenarios**:

1. **Given** 使用者在 Profile 頁面輸入正確的舊密碼與新密碼，**When** 提交變更，**Then** 系統更新密碼雜湊並登出使用者或更新 Session。
2. **Given** 使用者輸入已存在的使用者名稱，**When** 提交變更，**Then** 系統提示「使用者名稱已存在」。
3. **Given** 使用者更新地址、電話等基本資訊，**When** 提交儲存，**Then** 系統成功持久化這些變動。

---

### User Story 4 - 帳號刪除 (Priority: P3)

作為一名決定離開的使用者，我希望可以自主刪除（軟刪除）我的帳號，以保護我的隱私。

**Why this priority**: 符合隱私法規（如 GDPR）的基本要求，雖然使用頻率低但法律重要性高。

**Independent Test**: 獨立測試 `DELETE /me` 端點及其對後端資料狀態的影響（`deleted_at`, `is_active`）。

**Acceptance Scenarios**:

1. **Given** 使用者選擇刪除帳號，**When** 完成確認，**Then** 系統設定 `deleted_at` 為當下時間，標記 `is_active=False`，並將使用者登出。
2. **Given** 使用者已標記為軟刪除，**When** 嘗試再次登入，**Then** 系統應拒絕登入。

### Edge Cases

- **Token 過期**：當驗證信箱或重設密碼的 Token 超過時效，系統應引導使用者重新發起請求。
- **惡意請求**：對同一 Email 短時間內多次發起重設密碼請求，應有 Rate Limiting 保護。
- **密碼刪除驗證**：為了確保帳號安全，系統在執行帳號刪除（軟刪除）前，必須要求使用者輸入目前的密碼進行驗證。

## 3. Requirements

### Functional Requirements

- **FR-001**: 系統 MUST 在註冊時發送驗證郵件。
- **FR-002**: 系統 MUST 使用具有時效性的 Token（註冊驗證 24 小時，重設密碼 1 小時）。
- **FR-003**: 系統 MUST 實作密碼重設流程，且 Token 僅能使用一次。
- **FR-004**: 系統 MUST 在變更密碼時驗證舊密碼。
- **FR-005**: 系統 MUST 在變更使用者名稱時檢查唯一性。
- **FR-006**: 系統 MUST 支援軟刪除（Soft Delete），保留資料但禁止登入。
- **FR-007**: 系統 MUST 在非同步任務（Celery）中處理郵件發送。

### Key Entities

- **UserEntity**:
  - `is_active` (bool): 是否已啟用（Email 驗證後）。
  - `username` (string): 唯一的登入名稱。
  - `email` (string): 唯一的信箱位址。
  - `password_hash` (string): 加密儲存的密碼。
  - `deleted_at` (datetime, optional): 軟刪除時間戳記。
- **Tokens (Redis)**:
  - `registration_token`: 儲存註冊驗證狀態。
  - `reset_password_token`: 儲存密碼重設權利。

## 4. Success Criteria

### Measurable Outcomes

- **SC-001**: 使用者在收到信件後，點擊驗證到帳號啟用應在 3 秒內完成處理。
- **SC-002**: 忘記密碼請求在 5 秒內應能成功加入郵件發送隊列。
- **SC-003**: 99% 的合法密碼變更請求應能在 500ms 內完成。
- **SC-004**: 所有涉及安全的操作（變更密碼、刪除帳號）必須有完整的日誌紀錄。

## 5. Assumptions & Dependencies
- 郵件服務（如 Brevo/SendGrid）整合已就緒且可正常發送。
- Redis 端點已配置於環境變數。
- 前端頁面（Vue 3）需實作 `/email-verify` 與 `/reset-password` 對應路由。
