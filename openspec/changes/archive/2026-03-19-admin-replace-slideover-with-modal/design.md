## Context

後台目前有兩種互動模式：
1. **Sheet 側邊滑出**：`ProductManagementView.vue`（商品新增/編輯）、`OrderManagementView.vue`（訂單詳情/編輯）使用 `@/components/ui/sheet`。
2. **內嵌 Card**：`CategoryManagementView.vue` 的新增分類表單直接呈現在頁面左欄。

目標是統一改為居中彈出的 Dialog 模式。shadcn/ui 的 `ConfirmDialog.vue` 已使用 Radix UI Dialog，需確認 `@/components/ui/dialog` 是否存在，若無則需新增。

## Goals / Non-Goals

**Goals:**
- 三個管理視圖的新增/編輯/詳情均以居中 Dialog 呈現
- 複用現有 `ProductForm.vue`，不更動表單邏輯
- Dialog 需可捲動（商品表單內容較長）
- 保持現有 v-model:open 狀態管理模式不變

**Non-Goals:**
- 修改表單欄位、驗證邏輯或 API 呼叫
- 修改路由結構（不改為 URL-based modal）
- 重構 Pinia stores 或 services

## Decisions

### 1. 使用 shadcn/ui Dialog 元件

**決定**：以 `@/components/ui/dialog`（shadcn/ui Dialog）取代 Sheet。

**原因**：
- 與現有 `ConfirmDialog.vue` 使用相同底層（Radix UI Dialog），行為一致。
- 若 `dialog` 元件不存在，按 shadcn/ui 標準安裝即可，無額外依賴。
- Dialog 天生居中顯示，CSS 無需特別調整。

**替代方案**：自行用 `<div>` + fixed positioning 實作 Modal → 拒絕，重複造輪子且缺少 aria/focus trap。

### 2. Dialog 寬度設定

| 頁面 | 建議寬度 |
|------|---------|
| 商品新增/編輯 | `max-w-2xl`（需容納圖片上傳、多欄位） |
| 分類新增/編輯 | `max-w-md`（表單簡單，欄位少） |
| 訂單詳情/編輯 | `max-w-2xl`（需顯示商品列表、收件資訊） |

Dialog 內容加 `overflow-y-auto max-h-[80vh]` 確保內容過長時可捲動。

### 3. 分類管理的觸發方式

**現況**：分類表單為內嵌 Card，沒有 Sheet 觸發器。
**決定**：在分類列表操作列新增「新增分類」按鈕作為 Dialog 觸發器，移除左欄內嵌 Card，改為單欄全寬佈局。
**原因**：與商品、訂單管理的互動模式統一。

## Risks / Trade-offs

- **Dialog 元件不存在** → 需先執行 `npx shadcn-vue@latest add dialog`（或手動建立），確認後再實作三個視圖。
- **商品表單過長** → 已規劃 `max-h-[80vh] overflow-y-auto`，圖片上傳區仍可操作。
- **分類管理版型變更** → 移除雙欄 grid 改為單欄，視覺變化較大，但功能不受影響。
