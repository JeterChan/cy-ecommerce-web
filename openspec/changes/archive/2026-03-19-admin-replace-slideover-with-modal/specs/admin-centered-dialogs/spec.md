## ADDED Requirements

### Requirement: 商品新增/編輯使用居中 Dialog
後台商品管理頁面的新增與編輯操作 SHALL 以居中彈出 Dialog 呈現，取代原右側滑出 Sheet。Dialog 寬度為 `max-w-2xl`，內容區域需可捲動（`max-h-[80vh] overflow-y-auto`）。

#### Scenario: 點擊新增商品按鈕開啟 Dialog
- **WHEN** 管理員點擊「新增商品」按鈕
- **THEN** 頁面正中央彈出新增商品 Dialog，背景加上遮罩

#### Scenario: 點擊編輯商品按鈕開啟 Dialog
- **WHEN** 管理員點擊商品列表中的「編輯」按鈕
- **THEN** 頁面正中央彈出編輯商品 Dialog，並預填該商品資料

#### Scenario: 關閉 Dialog
- **WHEN** 管理員點擊 Dialog 右上角關閉按鈕、按下 ESC 鍵或點擊遮罩
- **THEN** Dialog 關閉，返回商品列表頁面

#### Scenario: 表單提交成功關閉 Dialog
- **WHEN** 管理員成功提交商品表單
- **THEN** Dialog 關閉，商品列表自動重新整理

### Requirement: 分類新增/編輯使用居中 Dialog
後台分類管理頁面的新增與編輯操作 SHALL 以居中彈出 Dialog 呈現，取代原內嵌 Card 表單。Dialog 寬度為 `max-w-md`。頁面改為單欄佈局，操作列包含「新增分類」觸發按鈕。

#### Scenario: 點擊新增分類按鈕開啟 Dialog
- **WHEN** 管理員點擊「新增分類」按鈕
- **THEN** 頁面正中央彈出新增分類 Dialog

#### Scenario: 點擊編輯分類按鈕開啟 Dialog
- **WHEN** 管理員點擊分類列表中的「編輯」按鈕
- **THEN** 頁面正中央彈出編輯分類 Dialog，並預填該分類資料

#### Scenario: 表單提交成功關閉 Dialog
- **WHEN** 管理員成功提交分類表單
- **THEN** Dialog 關閉，分類列表自動重新整理

### Requirement: 訂單詳情/編輯使用居中 Dialog
後台訂單管理頁面的訂單詳情與狀態編輯操作 SHALL 以居中彈出 Dialog 呈現，取代原右側滑出 Sheet。Dialog 寬度為 `max-w-2xl`，內容區域需可捲動（`max-h-[80vh] overflow-y-auto`）。

#### Scenario: 點擊訂單列表行開啟 Dialog
- **WHEN** 管理員點擊訂單列表中的任一訂單行或「查看」按鈕
- **THEN** 頁面正中央彈出訂單詳情 Dialog，顯示完整訂單資訊

#### Scenario: 訂單 Dialog 可更新狀態與備註
- **WHEN** 管理員在訂單 Dialog 中變更狀態或輸入備註並儲存
- **THEN** 系統呼叫 API 更新訂單，Dialog 顯示成功訊息

#### Scenario: 關閉訂單 Dialog
- **WHEN** 管理員點擊關閉按鈕或按 ESC
- **THEN** Dialog 關閉，返回訂單列表
