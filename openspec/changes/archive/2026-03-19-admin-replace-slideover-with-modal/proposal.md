## Why

後台管理的商品新增/編輯、分類管理及訂單詳情目前使用從右側滑入的 Sheet 面板（或內嵌 Card），這種互動方式在寬螢幕上會讓焦點偏離頁面中心，且不符合「彈出對話框」的用戶習慣。改成居中彈出視窗（Dialog/Modal）可提升操作一致性與視覺焦點。

## What Changes

- **商品管理**：將 `ProductManagementView.vue` 的 Sheet 面板替換為居中 Dialog，保留所有現有表單欄位與邏輯（`ProductForm.vue` 本身不變）。
- **分類管理**：將 `CategoryManagementView.vue` 的內嵌 Card 表單改為居中 Dialog，觸發按鈕放在頁面操作列。
- **訂單管理**：將 `OrderManagementView.vue` 的 Sheet 面板替換為居中 Dialog，保留訂單詳情顯示、狀態更新與備註功能。

## Capabilities

### New Capabilities

- `admin-centered-dialogs`：後台三個管理頁面的新增/編輯/詳情操作改以居中 Dialog 呈現，取代右側滑出 Sheet 與內嵌 Card。

### Modified Capabilities

## Impact

- 修改三個 Vue 視圖檔案：`ProductManagementView.vue`、`CategoryManagementView.vue`、`OrderManagementView.vue`
- 確認 `@/components/ui/dialog` shadcn/ui 元件已存在或需新增
- `ProductForm.vue` 本身不需修改，僅調整其容器
- 不影響 API、後端邏輯、路由或 Pinia stores
