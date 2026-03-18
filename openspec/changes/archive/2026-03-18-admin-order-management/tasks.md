## 1. 資料庫與模型擴展

- [x] 1.1 在 `OrderModel` 中新增 `admin_note` 與 `status_updated_at` 欄位
- [x] 1.2 更新 `OrderStatus` 枚舉以包含所有建議狀態（如 `refunding`, `refunded`）
- [x] 1.3 執行 Alembic 遷移以套用資料庫變更（或在開發環境自動重建）

## 2. 後端 API 實作

- [x] 2.1 建立 `admin_order_router` 並註冊至 `/api/v1/admin/orders`
- [x] 2.2 實作管理員訂單分頁列表 API，支援基本過濾（ID, 狀態）
- [x] 2.3 實作管理員訂單詳情 API，返回完整關聯資料與 `admin_note`
- [x] 2.4 實作訂單狀態更新 API，包含狀態轉換合法性校驗邏輯
- [x] 2.5 實作更新 `admin_note` 的獨立端點或整合至狀態更新 API
- [x] 2.6 為管理員訂單 API 編寫單元測試與整合測試

## 3. 前端管理介面實作

- [x] 3.1 在 `frontend/src/services/` 中新增 `adminOrderService`
- [x] 3.2 建立後台訂單管理列表頁面 (`AdminOrdersView.vue`)
- [x] 3.3 實作訂單列表的搜尋與狀態篩選功能
- [x] 3.4 實作訂單詳情 Modal，顯示詳細資訊與管理員備註
- [x] 3.5 實作訂單狀態更新功能（含二次確認彈窗）
- [x] 3.6 在管理後台導覽列中新增「訂單管理」連結


## 4. 驗證與存檔

- [x] 4.1 進行端到端 (E2E) 測試，確認管理員可正確更新訂單並查看歷史
- [x] 4.2 驗證普通用戶無法訪問 `/api/v1/admin/orders`
- [x] 4.3 執行 `/opsx:archive` 以存檔此變更
