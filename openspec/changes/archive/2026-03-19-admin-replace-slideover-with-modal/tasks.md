## 1. 安裝 Dialog 元件

- [x] 1.1 在 `frontend/` 目錄執行 `npx shadcn-vue@latest add dialog` 安裝 shadcn/ui Dialog 元件（將在 `src/components/ui/dialog/` 產生相關檔案）
- [x] 1.2 確認 `src/components/ui/dialog/index.ts` 已正確匯出 `Dialog`, `DialogContent`, `DialogHeader`, `DialogTitle`, `DialogDescription`

## 2. 商品管理改用 Dialog

- [x] 2.1 在 `src/views/admin/ProductManagementView.vue` 中，將 Sheet 相關 import 替換為 Dialog 元件 import
- [x] 2.2 將 `<Sheet v-model:open="isSheetOpen">` 與 `<SheetContent side="right" class="sm:max-w-2xl overflow-y-auto">` 替換為 `<Dialog v-model:open="isSheetOpen">` 與 `<DialogContent class="max-w-2xl max-h-[80vh] overflow-y-auto">`
- [x] 2.3 將 `<SheetHeader>` / `<SheetTitle>` 替換為 `<DialogHeader>` / `<DialogTitle>`
- [x] 2.4 移除 `<SheetTrigger>` wrapper，改為直接在「新增商品」Button 上加 `@click="openCreateSheet"` 綁定（維持現有邏輯不變）
- [x] 2.5 驗證：開啟新增商品 Dialog 顯示於頁面正中央；編輯商品 Dialog 可預填資料；提交後 Dialog 關閉且列表更新

## 3. 分類管理改用 Dialog

- [x] 3.1 在 `src/views/admin/CategoryManagementView.vue` 中新增 Dialog 相關 import，以及 `isDialogOpen` ref 狀態
- [x] 3.2 移除頁面左欄的內嵌新增分類 Card，改為單欄全寬佈局
- [x] 3.3 在操作列新增「新增分類」Button，點擊時開啟 Dialog
- [x] 3.4 將原新增分類表單內容移入 `<DialogContent class="max-w-md">` 中，並加上 `<DialogHeader>` / `<DialogTitle>`
- [x] 3.5 （後端無 updateCategory API，略過新增編輯按鈕）
- [x] 3.6 驗證：新增分類 Dialog 顯示於頁面正中央；提交後 Dialog 關閉且列表更新

## 4. 訂單管理改用 Dialog

- [x] 4.1 在 `src/views/admin/OrderManagementView.vue` 中，將 Sheet 相關 import 替換為 Dialog 元件 import
- [x] 4.2 將 `<Sheet v-model:open="isSheetOpen">` 與 `<SheetContent class="w-full sm:max-w-[600px] overflow-y-auto">` 替換為 `<Dialog v-model:open="isSheetOpen">` 與 `<DialogContent class="max-w-2xl max-h-[80vh] overflow-y-auto">`
- [x] 4.3 將 `<SheetHeader>` / `<SheetTitle>` / `<SheetDescription>` 替換為對應的 `<DialogHeader>` / `<DialogTitle>` / `<DialogDescription>`
- [x] 4.4 驗證：點擊訂單行開啟 Dialog 顯示於頁面正中央；狀態更新與備註儲存功能正常；Dialog 可正常關閉
