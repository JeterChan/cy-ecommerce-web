# order-checkout-system Specification

## Purpose
TBD - created by archiving change admin-order-management. Update Purpose after archive.
## Requirements
### Requirement: 訂單狀態追蹤增強
訂單系統 **SHALL** 記錄每次狀態變更的關鍵時間點，以供後台分析與流程監控。

#### Scenario: 記錄狀態更新時間
- **WHEN** 訂單狀態從 `pending` 變更為任何其他狀態（如 `paid`, `shipped`, `cancelled`）
- **THEN** 系統 **MUST** 自動更新 `status_updated_at` 欄位為當前伺服器時間

### Requirement: 訂單狀態枚舉定義
系統 **SHALL** 定義一組標準化的訂單狀態枚舉，涵蓋從下單到售後的全週期。

#### Scenario: 支援完整的訂單狀態
- **WHEN** 系統讀取或寫入訂單狀態時
- **THEN** 狀態 **MUST** 僅限於：`pending`, `paid`, `shipped`, `delivered`, `completed`, `cancelled`, `refunding`, `refunded`

### Requirement: 結帳流程 Redis 預扣前置檢查
結帳流程 **SHALL** 在進入 DB 悲觀鎖事務之前，先透過 `StockRedisService.try_deduct` 執行 Redis 庫存預扣。

#### Scenario: 預扣成功後進入 DB 事務
- **WHEN** 用戶發起結帳且所有購物車商品的 Redis 預扣均成功
- **THEN** 系統 **MUST** 繼續執行現有的 DB 悲觀鎖結帳流程（`SELECT ... FOR UPDATE`）

#### Scenario: 預扣失敗時跳過 DB 事務
- **WHEN** 用戶發起結帳且任一購物車商品的 Redis 預扣失敗
- **THEN** 系統 **MUST** 回滾所有已預扣的庫存並回傳 HTTP 400 庫存不足
- **AND** 不得進入 DB 事務，不佔用 DB 連線

#### Scenario: DB 事務異常後回滾 Redis
- **WHEN** Redis 預扣成功但 DB 事務拋出任何異常
- **THEN** 系統 **MUST** 在異常處理中呼叫 `StockRedisService.rollback` 回滾所有已預扣的庫存

