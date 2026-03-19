# admin-order-search Specification

## Purpose
提供後台管理員多欄位訂單搜尋功能，支援依訂單編號、收件人姓名、電話號碼及日期範圍篩選訂單，並在訂單列表表格中顯示收件人資訊。

## Requirements

### Requirement: 後端支援多欄位訂單搜尋參數
`GET /api/v1/admin/orders` SHALL 接受以下可選查詢參數：`search_order_number`（字串）、`search_recipient_name`（字串）、`search_phone`（字串）、`date_from`（日期）、`date_to`（日期）。所有新參數為可選，未提供時不影響查詢結果。

#### Scenario: 單一欄位搜尋
- **WHEN** 管理員傳送 `?search_order_number=ORD-2026`
- **THEN** 回傳所有 `order_number` 包含 `ORD-2026` 的訂單（不分大小寫）

#### Scenario: 多欄位組合搜尋
- **WHEN** 管理員傳送 `?search_recipient_name=張&status=PAID`
- **THEN** 回傳所有收件人姓名包含「張」且狀態為 PAID 的訂單

#### Scenario: 日期範圍搜尋（含當日）
- **WHEN** 管理員傳送 `?date_from=2026-03-01&date_to=2026-03-19`
- **THEN** 回傳 `created_at` 介於 `2026-03-01 00:00:00` 至 `2026-03-19 23:59:59.999999` 的訂單

#### Scenario: 空白參數不影響結果
- **WHEN** 管理員傳送 `?search_order_number=`（空字串）
- **THEN** 系統 SHALL 忽略此參數，等同未傳送

### Requirement: Repository 實作多欄位篩選
`IOrderRepository.list_all` 與 `count_all` SHALL 接受五個新可選參數，以 AND 邏輯組合所有非空條件。

#### Scenario: 所有條件 AND 組合
- **WHEN** 同時傳入 `search_recipient_name="王"` 與 `date_from=2026-03-01`
- **THEN** 只回傳「收件人姓名含王」且「建立日期 >= 2026-03-01」的訂單

#### Scenario: 無條件回傳全部
- **WHEN** 所有篩選參數皆為 None
- **THEN** 回傳全部訂單（分頁內）

### Requirement: 前端多欄位搜尋表單
後台訂單管理頁面 SHALL 提供獨立輸入欄位：訂單編號、收件人姓名、電話號碼、開始日期、結束日期、訂單狀態（下拉）。

#### Scenario: 點擊搜尋按鈕觸發查詢
- **WHEN** 管理員填入一或多個欄位後點擊「搜尋」按鈕
- **THEN** 系統 SHALL 重置至第 1 頁並依填入條件查詢

#### Scenario: Enter 鍵觸發搜尋
- **WHEN** 管理員在任一文字欄位按下 Enter 鍵
- **THEN** 系統 SHALL 觸發搜尋（等同點擊搜尋按鈕）

#### Scenario: 重置篩選
- **WHEN** 管理員點擊「重置篩選」按鈕
- **THEN** 系統 SHALL 清空所有搜尋欄位並重新查詢全部訂單

### Requirement: 訂單列表表格顯示收件人欄位
後台訂單列表表格 SHALL 在「訂單編號」欄位後顯示「收件人」欄，內容為 `recipient_name`。

#### Scenario: 列表顯示收件人姓名
- **WHEN** 訂單列表載入完成
- **THEN** 每筆訂單列顯示對應的 `recipient_name`
