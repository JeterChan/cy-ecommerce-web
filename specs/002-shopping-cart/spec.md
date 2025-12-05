# Feature Specification: Shopping Cart & Add to Cart

**Feature Branch**: `002-shopping-cart`
**Created**: 2025-12-03
**Status**: Draft
**Input**: User description: "建立商品模組的頁面，在商品詳情頁面添加數量以及按鈕提供使用者可以選擇數量，並提供 Button 將商品添加至購物車。在 Navbar 中添加購物車的 icon 和 Button, 提供使用者可以點擊購物車 Button 跳轉到購物車頁面。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 將商品加入購物車 (Priority: P1)

作為一名訪客，我希望能在商品詳情頁選擇購買數量並將商品加入購物車，以便稍後進行結帳。

**Why this priority**: 這是電子商務網站的核心轉換行為，沒有加入購物車的功能，使用者無法進行購買流程。

**Independent Test**: 進入商品詳情頁，選擇數量大於 1，點擊「加入購物車」，驗證系統記錄了該商品與正確數量 (可透過 UI 反饋或 Console 驗證)。

**Acceptance Scenarios**:

1. **Given** 使用者在商品詳情頁, **When** 使用者選擇數量 (例如 2) 並點擊「加入購物車」, **Then** 系統應將該商品及數量加入購物車狀態，並顯示成功提示 (如 Toast 訊息)。
2. **Given** 使用者已將某商品加入購物車, **When** 使用者再次將同商品加入購物車 (數量 1), **Then** 購物車內該商品的數量應累加 (原數量 + 1)。
3. **Given** 使用者嘗試輸入無效數量 (如 0 或負數), **When** 嘗試加入購物車, **Then** 系統應阻止操作並提示數量必須大於 0。

---

### User Story 2 - 透過 Navbar 進入購物車 (Priority: P2)

作為一名訪客，我希望能透過網站導覽列 (Navbar) 隨時查看並進入購物車頁面，以便確認我挑選的商品。

**Why this priority**: 提供全站通用的購物車入口是電商網站的標準導航體驗，確保使用者不會迷路。

**Independent Test**: 在網站任一頁面點擊 Navbar 上的購物車圖示，驗證是否成功導航至購物車頁面。

**Acceptance Scenarios**:

1. **Given** 使用者在首頁或商品頁, **When** 查看 Navbar, **Then** 應顯示購物車圖示/按鈕。
2. **Given** 購物車內有商品, **When** 使用者查看 Navbar 購物車圖示, **Then** 圖示旁應顯示當前購物車內的商品總數 (Badge)。
3. **Given** 使用者點擊 Navbar 購物車圖示, **When** 觸發點擊, **Then** 瀏覽器導航至購物車頁面 (`/cart`)。

---

### User Story 3 - 瀏覽購物車內容 (Priority: P3)

作為一名訪客，我希望能看見購物車頁面列出我已加入的所有商品及其數量與價格，以便核對購買清單。

**Why this priority**: 使用者在結帳前必須能檢視與確認購買內容，這是「購物車頁面」的基本功能。

**Independent Test**: 預先加入幾項商品至購物車，進入購物車頁面，驗證列表是否正確顯示商品名稱、單價、選擇數量與小計。

**Acceptance Scenarios**:

1. **Given** 購物車內有多項商品, **When** 使用者進入購物車頁面, **Then** 應顯示商品列表，每列包含圖片、名稱、單價、數量與小計。
2. **Given** 購物車是空的, **When** 使用者進入購物車頁面, **Then** 應顯示「購物車目前是空的」友善提示，並提供「去購物」的連結按鈕。

### Edge Cases

- **庫存限制**: 當使用者選擇的數量超過庫存時，應顯示錯誤提示 (本階段若無後端庫存，可暫忽略或設死上限)。
- **最大數量**: 防止惡意輸入極大數量導致數值溢出或 UI 跑版。
- **頁面刷新**: 在未登入狀態下刷新頁面，購物車內容應保留 (需使用 LocalStorage 或 Session)。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 商品詳情頁必須提供「數量選擇器」 (Quantity Selector)，允許使用者增減購買數量 (預設為 1)。
- **FR-002**: 商品詳情頁必須提供「加入購物車」按鈕 (Add to Cart Button)。
- **FR-003**: 系統必須實作「購物車狀態管理」(Cart State Management)，支援新增商品、更新數量、計算總價、移除商品。
- **FR-004**: 系統必須將購物車狀態持久化 (Persistence)，確保重新整理頁面後資料不丟失 (例如使用 LocalStorage)。
- **FR-005**: Navbar 必須包含購物車按鈕，並動態顯示當前購物車內的商品總件數。
- **FR-006**: 必須建立「購物車頁面」 (`/cart`)，並在該頁面顯示已加入的商品清單。
- **FR-007**: 購物車頁面的商品列表需顯示：商品圖片、名稱、單價、數量、小計。
- **FR-008**: 購物車頁面必須具備響應式設計 (Responsive Design)，在行動裝置上應以堆疊 (Stack) 或卡片方式呈現商品列表，確保資訊易讀。
- **FR-009**: 當系統讀取商品資訊或更新購物車狀態時，必須顯示適當的載入狀態 (Loading State) 或骨架屏 (Skeleton)，避免使用者操作未完成的介面。

### Key Entities *(include if feature involves data)*

- **CartItem (購物車項目)**:
  - `productId`: 關聯的商品 ID
  - `quantity`: 購買數量 (Integer, > 0)
  - `addedAt`: 加入時間 (Timestamp, Optional for sorting)
  
- **Cart (購物車)**:
  - `items`: List<CartItem>
  - `totalQuantity`: 商品總件數 (Derived)
  - `totalAmount`: 總金額 (Derived)

## Assumptions & Dependencies

- **Assumptions**:
  - 暫不需實作「結帳 (Checkout)」流程，本功能僅止於購物車頁面瀏覽。
  - 暫不需實作「後端同步」，購物車資料優先存放於 Client 端 (LocalStorage)。
  - 商品資訊 (價格、名稱) 在加入購物車時可能需快照 (Snapshot) 或動態透過 Product ID 查詢，MVP 採動態查詢或簡單快照皆可。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 使用者點擊「加入購物車」後，Navbar 購物車圖示的數字更新延遲小於 100ms。
- **SC-002**: 購物車資料在瀏覽器關閉重開後 100% 仍保留 (LocalStorage 驗證)。
- **SC-003**: 在商品詳情頁的操作流程 (選擇數量 -> 加入) 可透過鍵盤完全操作 (Accessibility)。
- **SC-004**: 購物車頁面載入時間 (LCP) 小於 1.5 秒。