# Feature Specification: Backend Cart Merge System

**Feature Branch**: `009-cart-merge-system`  
**Created**: 2026-01-25  
**Status**: Draft  
**Input**: User description: "建立後端購物車系統，分辨訪客購物車與會員購物車，並且當訪客添加商品至購物車，但又登入成會員，將身為訪客時的購物車與會員的購物車合併。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 訪客購物車管理 (Priority: P1)

身為訪客，我可以新增、修改、刪除購物車內的商品，以便在不登入的情況下進行選購。

**Why this priority**: 這是電子商務網站最基礎的功能，允許潛在客戶在註冊前先體驗購物流程。

**Independent Test**: 可以完全獨立測試訪客流程：在不登入的狀態下使用 API 加入商品，確認商品存在於回傳的購物車資訊中。

**Acceptance Scenarios**:

1. **Given** 我是未登入的訪客, **When** 我將商品加入購物車, **Then** 系統應建立一個與我的工作階段 (Session) 關聯的臨時購物車，並包含該商品。
2. **Given** 我的訪客購物車已有商品 A (數量 1), **When** 我再次加入商品 A (數量 2), **Then** 購物車內商品 A 的數量應更新為 3。
3. **Given** 訪客購物車有商品, **When** 我請求檢視購物車, **Then** 系統回傳正確的商品列表與總金額。

---

### User Story 2 - 會員購物車管理 (Priority: P1)

身為會員，我可以管理我的購物車，且購物車內容會永久保存，不隨工作階段結束而消失。

**Why this priority**: 確保忠實客戶的購物意向被保留，提供跨裝置的購物體驗。

**Independent Test**: 使用會員 Token 呼叫 API，確認購物車內容與會員帳號綁定，而非僅與 Session 綁定。

**Acceptance Scenarios**:

1. **Given** 我是已登入會員, **When** 我加入商品並登出，再重新登入, **Then** 購物車內該商品仍然存在。
2. **Given** 我是已登入會員, **When** 我移除購物車內的商品, **Then** 資料庫中的會員購物車紀錄應同步更新。

---

### User Story 3 - 登入時合併購物車 (Priority: P1)

身為已將商品加入購物車的訪客，當我登入時，我的訪客購物車內容會自動合併至我的會員購物車，確保選購的商品不會遺失。

**Why this priority**: 這是連接訪客與會員體驗的關鍵，防止使用者因登入而遺失已選商品，提升轉換率。

**Independent Test**: 模擬訪客加入商品 -> 執行登入 API -> 檢查會員購物車內容是否包含原有訪客商品。

**Acceptance Scenarios**:

1. **Given** 訪客購物車有商品 A (數量 1), 會員購物車是空的, **When** 我登入會員帳號, **Then** 會員購物車應包含商品 A (數量 1)，且訪客購物車被清空。
2. **Given** 訪客購物車有商品 A (數量 2), 會員購物車已有商品 A (數量 3), **When** 我登入會員帳號, **Then** 會員購物車內商品 A 的數量應合併為 5。
3. **Given** 訪客購物車有商品 B, 會員購物車有商品 A, **When** 我登入會員帳號, **Then** 會員購物車應同時包含商品 A 與商品 B。

### Edge Cases

- 當訪客 Session 過期後，嘗試存取購物車應建立新的空購物車。
- 當商品庫存不足時，合併過程應如何處理？(假設：仍合併入購物車，但標示庫存不足或於結帳時檢查)。
- 訪客與會員購物車商品數量加總超過系統限制 (若有) 時的處理。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系統 MUST 能透過 Session ID 或暫存 Token 識別訪客，並建立/讀取對應的購物車資料。
- **FR-002**: 系統 MUST 能透過 User ID 識別會員，並建立/讀取對應的持久化購物車資料。
- **FR-003**: 系統 MUST 支援「加入商品」操作：若商品不存在則新增，若已存在則增加數量。
- **FR-004**: 系統 MUST 支援「更新數量」與「移除商品」操作。
- **FR-005**: 系統 MUST 在訪客執行登入 (Login) 成功後，自動觸發購物車合併程序。
- **FR-006**: 合併邏輯 MUST 為：將訪客購物車的所有項目移至會員購物車；若同一商品 ID 已存在，則將數量相加。
- **FR-007**: 合併成功後，系統 MUST 清空或刪除原有的訪客購物車資料，避免重複處理。
- **FR-008**: 系統 MUST 在回傳購物車資訊時，包含商品詳細資訊 (如名稱、價格、圖片)。

### Key Entities *(include if feature involves data)*

- **Cart**: 購物車主體，包含 ID, UserID (Nullable, for members), SessionID (Nullable, for guests), CreatedAt, UpdatedAt。
- **CartItem**: 購物車明細，包含 ID, CartID, ProductID, Quantity, AddedAt。
- **Product**: 商品資訊 (唯讀引用)，用於顯示名稱與計算價格。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 訪客在未登入狀態下，關閉瀏覽器後重新打開 (在系統設定的有效期間內)，購物車內容保持一致。
- **SC-002**: 100% 的訪客購物車商品在登入後成功轉移至會員購物車，無資料遺失。
- **SC-003**: 當發生重複商品合併時，數量計算準確度為 100%。
- **SC-004**: 購物車 API (新增/查詢/修改) 平均回應時間 < 200ms。
- **SC-005**: 支援至少 100 個併發使用者同時進行購物車操作而不發生資料衝突。