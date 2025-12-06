# Feature Specification: 建立訂單流程

**Feature Branch**: `003-checkout-flow`  
**Created**: 2025-12-05  
**Status**: Draft  
**Input**: User description: "建立訂單流程，使用者可以從購物車介面按下前往結帳的Button，訂單介面提供使用者訂單明細、讓使用者可以填寫郵寄資訊、收件人、購買人資訊，訂單備註、寄送方式(宅配,7-11店到店)、付款方式(信用卡、貨到付款、匯款/轉帳)。"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - 檢視訂單明細與啟動結帳 (Priority: P1)

使用者從購物車確認商品後，進入結帳頁面查看詳細的訂單內容，確保購買品項正確。

**Why this priority**: 這是結帳流程的入口，使用者必須先確認購買內容才能進行後續動作。

**Independent Test**: 使用者點擊結帳按鈕後，能成功導向結帳頁面並顯示正確的商品清單與金額。

**Acceptance Scenarios**:

1. **Given** 購物車內有商品, **When** 使用者點擊「前往結帳」按鈕, **Then** 系統導向至結帳頁面
2. **Given** 使用者在結帳頁面, **When** 頁面載入完成, **Then** 顯示所有購買商品的名稱、數量、單價及總金額

---

### User Story 2 - 填寫訂購與運送資訊 (Priority: P1)

使用者在結帳頁面填寫購買人與收件人的相關資料，並選擇運送方式（宅配或超商取貨）。

**Why this priority**: 收集正確的配送資訊是完成交易並交付商品的核心需求。

**Independent Test**: 使用者能填寫表單並選擇運送方式，系統能正確驗證欄位有效性。

**Acceptance Scenarios**:

1. **Given** 使用者在結帳頁面, **When** 填寫購買人與收件人姓名、電話, **Then** 系統暫存或接受該資訊
2. **Given** 使用者選擇「宅配」, **When** 未填寫地址, **Then** 系統提示地址為必填
3. **Given** 使用者選擇「7-11店到店」, **When** 未選擇門市, **Then** 系統提示門市資訊為必填
4. **Given** 使用者希望留言, **When** 填寫訂單備註, **Then** 系統記錄該備註內容

---

### User Story 3 - 選擇付款方式並完成訂單 (Priority: P1)

使用者選擇偏好的付款方式（信用卡、貨到付款、匯款）並送出訂單，完成購買流程。

**Why this priority**: 完成付款選擇與訂單建立是交易的最終步驟，直接關係到營收與庫存扣減。

**Independent Test**: 使用者選擇不同付款方式後能成功送出訂單，並看到完成畫面。

**Acceptance Scenarios**:

1. **Given** 所有必填資訊皆已填寫, **When** 使用者選擇「信用卡」並送出, **Then** 系統導向至信用卡付款/輸入介面
2. **Given** 所有必填資訊皆已填寫, **When** 使用者選擇「貨到付款」或「匯款/轉帳」並送出, **Then** 系統建立訂單並顯示完成頁面（包含匯款資訊若適用）
3. **Given** 訂單成功建立, **When** 流程結束, **Then** 購物車內容被清空且使用者收到訂單確認

---

### Edge Cases

- 若在填寫過程中商品庫存不足，系統應阻擋結帳並提示使用者。
- 若使用者輸入無效的電話號碼或 Email 格式，系統應即時驗證錯誤。
- 若付款過程中網路中斷，系統應確保訂單狀態明確（未付款或付款失敗），避免重複扣款或掉單。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系統必須提供「前往結帳」按鈕於購物車介面。
- **FR-002**: 結帳頁面必須顯示訂單明細，包含商品名稱、屬性、單價、數量、小計與總金額。
- **FR-003**: 系統必須允許使用者輸入購買人資訊（姓名、電話）。
- **FR-004**: 系統必須允許使用者輸入收件人資訊（姓名、電話）。
- **FR-005**: 系統必須提供「宅配」與「7-11店到店」兩種寄送方式選項。
- **FR-006**: 當選擇「宅配」時，系統必須要求使用者輸入郵寄地址。
- **FR-007**: 當選擇「7-11店到店」時，系統必須要求使用者輸入或選擇門市資訊。
- **FR-008**: 系統必須提供「信用卡」、「貨到付款」、「匯款/轉帳」三種付款方式選項。
- **FR-009**: 系統必須允許使用者輸入選填的「訂單備註」。
- **FR-010**: 系統必須在送出訂單前驗證所有必填欄位的完整性與格式正確性。
- **FR-011**: 訂單建立後，系統必須清空該使用者的購物車。

### Key Entities *(include if feature involves data)*

- **訂單 (Order)**: 代表一筆交易，包含 ID、購買人 ID、狀態（待付款、處理中等）、總金額、建立時間、備註。
- **訂單細項 (OrderItem)**: 訂單內的個別商品資訊，包含商品 ID、當下單價、數量。
- **收件資訊 (ShippingInfo)**: 包含收件人姓名、電話、運送方式（Type）、地址或門市資訊。
- **購買人資訊 (PurchaserInfo)**: 包含購買人姓名、電話。
- **付款資訊 (PaymentInfo)**: 包含付款方式（Method）、付款狀態。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 使用者從進入結帳頁面到完成訂單的平均時間低於 3 分鐘。
- **SC-002**: 系統能處理 100% 的有效訂單請求，無資料遺失。
- **SC-003**: 95% 的使用者在第一次嘗試時能成功通過表單驗證（無驗證錯誤）。
- **SC-004**: 訂單建立後，資料庫中必須包含完整的運送與付款偏好紀錄。