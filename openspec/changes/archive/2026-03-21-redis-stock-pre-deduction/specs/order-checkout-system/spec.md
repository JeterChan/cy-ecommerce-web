## ADDED Requirements

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
