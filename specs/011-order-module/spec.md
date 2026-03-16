# Feature Specification: Order Module

**Feature Branch**: `011-order-module`
**Created**: 2026-02-21
**Status**: Draft
**Input**: User description: "開發訂單模組，使用者成功送出訂單後，需要清空購物車，並且儲存訂單至資料庫。建立訂單的 CRUD 功能。在使用者要結帳時，將商品價格快取儲存。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 送出訂單 (Priority: P1)

作為一名使用者，我希望能夠送出購物車中的商品建立訂單，以便完成購買。

**Why this priority**: 這是電商平台的核心功能，讓使用者完成交易，沒有此功能無法產生營收。

**Independent Test**: 使用者將商品加入購物車後，點擊結帳並送出訂單，驗證資料庫中是否有新增訂單，且購物車是否被清空。

**Acceptance Scenarios**:

1. **Given** 使用者購物車內有商品, **When** 使用者送出訂單, **Then** 系統建立一筆新訂單，包含所有購物車內的商品項目。
2. **Given** 使用者成功送出訂單, **When** 訂單建立完成, **Then** 系統清空該使用者的購物車。
3. **Given** 使用者準備結帳, **When** 建立訂單時, **Then** 系統將當下的商品價格快取 (Snapshot) 至訂單項目中，即使後續商品價格變動，訂單金額不受影響。

---

### User Story 2 - 查看訂單列表與詳情 (Priority: P2)

作為一名使用者，我希望能查看我的歷史訂單，以便了解我的購買紀錄與訂單狀態。

**Why this priority**: 讓使用者追蹤訂單狀態與消費紀錄，提升使用者信任感。

**Independent Test**: 建立訂單後，呼叫訂單列表 API 或進入訂單頁面，驗證是否顯示該筆訂單及其正確內容。

**Acceptance Scenarios**:

1. **Given** 使用者已登入且有歷史訂單, **When** 使用者查看訂單列表, **Then** 顯示所有該使用者的訂單摘要 (如訂單編號、日期、總金額、狀態)。
2. **Given** 使用者在訂單列表, **When** 點擊某筆訂單, **Then** 顯示該訂單的詳細資訊 (包含當時購買的價格、數量、總金額、收件資訊等)。

---

### User Story 3 - 訂單管理 CRUD (Priority: P3)

作為系統管理員 (或是後端系統流程)，我需要能對訂單進行基本的建立、讀取、更新、刪除 (CRUD) 操作，以便維護訂單狀態與處理異常。

**Why this priority**: 系統維護與客戶服務需求，例如更新訂單狀態 (已付款、已出貨) 或取消無效訂單。

**Independent Test**: 使用 API 建立、讀取、更新、刪除 (或軟刪除) 訂單，驗證資料庫狀態變化。

**Acceptance Scenarios**:

1. **Given** 一筆已存在的訂單, **When** 管理員/系統更新訂單狀態 (如：從「待付款」改為「已付款」), **Then** 系統更新該訂單的狀態欄位，並記錄更新時間。
2. **Given** 一筆訂單, **When** 管理員/使用者取消訂單, **Then** 訂單狀態變更為「已取消」，且庫存 (若有扣除) 應相應處理 (視庫存策略而定，此處專注於狀態變更)。

### Edge Cases

- **庫存不足**: 當使用者送出訂單時，若部分商品庫存不足，應阻擋訂單建立並提示使用者哪些商品缺貨。
- **重複送單 (Double Submit)**: 避免使用者因網絡延遲或重複點擊導致建立多筆相同訂單 (需有防止重複機制)。
- **價格變動**: 使用者將商品加入購物車後，若後台價格調整，在結帳建立訂單的當下，應以當時系統顯示的價格或最新價格為準 (本規格要求快取結帳當下價格)。
- **交易失敗**: 若訂單主檔建立成功但明細建立失敗，或扣庫存失敗，應取消整個交易，確保資料一致性。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系統必須提供建立訂單的功能，接收使用者購物車資訊並生成訂單。
- **FR-002**: 系統在成功建立訂單後，必須自動清空該使用者的購物車內容。
- **FR-003**: 系統必須將訂單資訊持久化至資料庫，包含訂單 ID、使用者 ID、總金額、建立時間、狀態等。
- **FR-004**: 系統必須在建立訂單時，將每個商品的當前價格記錄在訂單項目 (Order Item) 中 (Price Snapshot)，不可直接關聯商品資料表中的浮動價格。
- **FR-005**: 系統必須提供查詢單一訂單詳情的介面，回傳包含訂單主檔與明細的完整資訊。
- **FR-006**: 系統必須提供查詢特定使用者所有訂單列表的介面，支援基本的分頁或排序。
- **FR-007**: 系統必須提供更新訂單狀態的介面 (例如：Pending, Paid, Shipped, Cancelled, Refunded)。
- **FR-008**: 系統必須驗證訂單資料的完整性，確保訂單總金額等於各明細小計 (單價 x 數量) 之總和 (或是包含運費/折扣後的正確金額)。

### Key Entities *(include if feature involves data)*

- **Order (訂單主檔)**:
  - `id`: 唯一識別碼
  - `user_id`: 購買者 ID (關聯 User)
  - `total_amount`: 訂單總金額
  - `status`: 訂單狀態 (Enum: PENDING, PAID, SHIPPED, COMPLETED, CANCELLED)
  - `created_at`: 建立時間
  - `updated_at`: 更新時間

- **OrderItem (訂單明細)**:
  - `id`: 唯一識別碼
  - `order_id`: 關聯的訂單 ID
  - `product_id`: 商品 ID
  - `quantity`: 購買數量
  - `price`: 購買時的單價 (Snapshot Price)

## Assumptions & Dependencies

- **Assumptions**:
  - 使用者必須先登入才能建立訂單。
  - 購物車模組已存在且能提供購物車內容。
  - 商品資料 (名稱、價格、庫存) 已存在於系統中。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 使用者成功送出訂單後，購物車項目數歸零，資料庫中新增一筆對應的訂單資料。
- **SC-002**: 訂單建立後，即使商品原價修改，查詢訂單詳情時仍顯示購買當下的價格 (Price Snapshot 驗證)。
- **SC-003**: 訂單建立 API 回應時間在 95% 的情況下小於 2 秒 (高併發下需維持穩定)。
- **SC-004**: 完整的訂單 CRUD 功能 (Create, Read, Update, Delete/Cancel) 皆可通過 API 自動化測試驗證。