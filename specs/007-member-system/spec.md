# 功能規格: 會員系統 (Member System)

**功能分支**: `007-member-system`  
**建立日期**: 2026年1月14日 星期三  
**狀態**: 草稿  
**輸入**: 使用者描述: "使用 Vue.js 建立會員系統, 包含登入,註冊,記住我,登出,忘記密碼功能。註冊頁面要包含: email, password, username. 密碼需要重複輸入一次確認是否正確。註冊頁面要對 email 和 password 進行格式驗證, 密碼至少要8位且至少一個大寫字母、特殊字元。登入頁面要有記住我和忘記密碼的功能。點擊忘記密碼會導轉到忘記密碼的頁面。在註冊和登入頁面，都需要將密碼遮蔽，也提供使用者可以選擇要遮蔽還是顯示。成功登入後，在 header 顯示該使用者的 username. 並且點擊 username 的 icon 會跳出下拉選單, 有個人檔案, 登出等功能。驗證系統是採用 JWT Authentication."

## 釐清事項 (Clarifications)

### Session 2026-01-14

- Q: How should the database schema be initialized in the Development environment, and should I generate the missing Alembic script for Production? → A: User will handle Prod migrations manually. Backend service is ready.
- Q: How should API/Validation errors be displayed? → A: Toasts (Notifications) for global API errors, Inline for form validation errors.
- Q: Should we use a standardized validation library or implement manual validation logic? → A: Library (VeeValidate + Zod).
- Q: For managing UI text, should we implement an internationalization (i18n) library now, or directly embed Traditional Chinese strings within Vue components? → A: Use `vue-i18n`.

## 使用者情境與測試 *(必填)*

### 使用者故事 1 - 註冊 (優先級: P1)

身為一個訪客，我想要註冊一個帳戶，以便成為會員並使用會員功能。

**為何此優先級**: 這是獲取使用者的主要入口。

**獨立測試**: 可以透過填寫註冊表單並提交，驗證是否成功建立帳戶。

**驗收情境**:

1. **情境**：訪客在註冊頁面，**當**輸入有效的 Username, Email, Password (並重複輸入確認) 並提交，**則**系統建立帳戶並自動登入或導向登入頁。
2. **情境**：訪客，**當**輸入無效的 Email 或密碼強度不足 (未滿8位、無大寫或無特殊字元)，**則**系統顯示格式錯誤提示 (Inline)，不予提交。
3. **情境**：訪客，**當**兩次輸入的密碼不一致，**則**系統顯示密碼不匹配錯誤 (Inline)。
4. **情境**：訪客，**當**點擊密碼欄位旁的「顯示/隱藏」按鈕，**則**密碼內容在明文與遮蔽狀態間切換。

---

### 使用者故事 2 - 登入 (優先級: P1)

身為一個會員，我想要登入我的帳戶，以便存取我的個人資料和功能。

**為何此優先級**: 存取受保護功能的必要條件。

**獨立測試**: 可以透過輸入正確憑證登入，驗證是否獲得授權並進入首頁。

**驗收情境**:

1. **情境**：會員在登入頁面，**當**輸入正確的 Email 和 Password 並提交，**則**成功登入並跳轉至首頁。
2. **情境**：會員，**當**勾選「記住我」並登入，**則**關閉瀏覽器後重開仍保持登入狀態。
3. **情境**：會員，**當**點擊「忘記密碼」連結，**則**導向至忘記密碼頁面。
4. **情境**：會員，**當**操作密碼顯示功能，**則**可查看輸入的密碼。
5. **情境**：會員，**當**登入失敗 (API 錯誤)，**則**系統顯示全域通知 (Toast) 提示錯誤原因。

---

### 使用者故事 3 - 會員選單與登出 (優先級: P2)

身為一個已登入的會員，我想要在頁面頂部看到我的身份並能登出，以便管理我的會話。

**為何此優先級**: 提供使用者狀態回饋與安全退出的機制。

**獨立測試**: 登入後檢查 Header，點擊選單並登出，驗證是否回到未登入狀態。

**驗收情境**:

1. **情境**：已登入會員，**當**瀏覽網站時，**則** Header 顯示使用者的 Username。
2. **情境**：已登入會員，**當**點擊 Username 圖示/名稱，**則**顯示下拉選單 (包含個人檔案、登出)。
3. **情境**：已登入會員，**當**點擊「登出」，**則**清除登入狀態 (JWT) 並導向回登入頁或首頁。

---

### 邊緣案例

- **JWT 過期**：使用者在操作期間若 Token 過期，應被提示重新登入或自動導向登入頁 (Toast)。
- **帳號重複**：註冊時若 Email 或 Username 已存在，應顯示明確錯誤訊息 (Toast 或 Inline)。
- **網路錯誤**：登入或註冊過程中若發生網路斷線，應顯示友善錯誤提示 (Toast) 而非崩潰。

## 需求 *(必填)*

### 功能需求

- **FR-001**: 系統**必須**提供註冊介面，包含 Email, Password, Confirm Password, Username 欄位。
- **FR-002**: 系統**必須**驗證 Email 格式的正確性。
- **FR-003**: 系統**必須**強制密碼強度：至少 8 碼，包含至少一個大寫字母與一個特殊字元。
- **FR-004**: 系統**必須**在註冊時驗證「確認密碼」與「密碼」是否一致。
- **FR-005**: 註冊與登入介面的密碼欄位**必須**具備切換顯示/隱藏內容的功能。
- **FR-006**: 系統**必須**提供登入介面，包含 Email, Password 欄位與「記住我」選項。
- **FR-007**: 系統**必須**在登入介面提供「忘記密碼」連結，點擊後導向專屬頁面。
- **FR-008**: 系統**必須**在使用者成功登入後，於全站 Header 顯示其 Username。
- **FR-009**: 系統**必須**在 Header 提供使用者下拉選單，選項至少包含「個人檔案」與「登出」。
- **FR-010**: 執行「登出」動作**必須**完全清除客戶端的登入狀態與憑證 (Token)。
- **FR-011**: 系統驗證機制**必須**採用 JWT (JSON Web Token) 標準。
- **FR-012**: 系統**必須**將表單驗證錯誤 (如格式不符) 顯示於對應欄位旁 (Inline)，並將系統/API 錯誤 (如網路問題、登入失敗) 透過全域通知 (Toast) 顯示。
- **FR-013**: 前端表單驗證**必須**使用標準化驗證函式庫 (`VeeValidate` 結合 `Zod`) 進行實作。
- **FR-014**: 前端 UI 文本**必須**透過國際化 (i18n) 函式庫 (`vue-i18n`) 進行管理。

### 關鍵實體

- **User**: 使用者帳戶，包含 Username, Email, Password (加密儲存)。
- **Auth Token**: 用於驗證身分的權杖 (如 JWT)。

## 成功標準 *(必填)*

### 可衡量成果

- **SC-001**: 使用者註冊流程 (填寫至提交成功) 可在 2 分鐘內完成。
- **SC-002**: 密碼強度與格式驗證應在使用者輸入或離開欄位時即時反饋 (延遲 < 0.5秒)。
- **SC-003**: 勾選「記住我」後，使用者會話在關閉瀏覽器後至少保持 7 天有效 (除非主動登出)。
- **SC-004**: 登出操作應立即生效，舊的 Access Token 在客戶端失效。
