## Why

目前結帳流程使用 PostgreSQL 悲觀鎖 (`SELECT ... FOR UPDATE`) 保護庫存扣減，所有併發請求都必須進入 DB 排隊等待行鎖。壓力測試顯示 2000 VU 搶購 10 個庫存時，1990 個注定失敗的請求仍需等待數秒才能得知庫存不足。透過 Redis `DECRBY` 原子操作在 DB 之前預先過濾，可將失敗請求的回應時間從秒級降到毫秒級，同時大幅減輕 DB 鎖壓力。

## What Changes

- 新增 Redis 庫存預扣層：在進入 DB 事務前，使用 Redis `DECRBY` 原子扣減庫存，結果 < 0 則立即返回庫存不足
- 新增庫存初始化機制：商品建立/更新庫存時，同步將庫存數量寫入 Redis key `stock:{product_id}`
- 修改 `CheckoutUseCase.execute()`：在 `_perform_checkout` 前加入 Redis 預扣邏輯，DB 事務失敗時回滾 Redis 庫存（`INCRBY`）
- 修改商品管理（Admin 更新庫存）：庫存變更時同步更新 Redis

## Capabilities

### New Capabilities
- `redis-stock-guard`: Redis 預扣庫存機制，包含原子扣減、失敗回滾、庫存同步

### Modified Capabilities
- `order-checkout-system`: 結帳流程新增 Redis 預扣庫存前置檢查，DB 層悲觀鎖保留作為最終防線

## Impact

- **後端程式碼**：`checkout.py`（核心流程變更）、商品相關 use case（庫存同步）
- **基礎設施**：Redis 新增 `stock:{product_id}` key pattern
- **API 行為**：無 breaking change，回應格式不變，只是庫存不足的回應速度大幅提升
- **依賴**：無新依賴，使用現有 Redis 連線
