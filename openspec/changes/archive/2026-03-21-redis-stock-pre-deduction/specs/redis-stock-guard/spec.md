## ADDED Requirements

### Requirement: Redis 庫存原子預扣
系統 **SHALL** 在結帳請求進入 DB 事務之前，使用 Redis `DECRBY` 原子操作預扣庫存，過濾掉庫存不足的請求。

#### Scenario: 庫存充足時預扣成功
- **WHEN** 用戶結帳且 Redis `DECRBY stock:{product_id} quantity` 回傳值 >= 0
- **THEN** 系統 **MUST** 允許該請求繼續進入 DB 事務建立訂單

#### Scenario: 庫存不足時立即拒絕
- **WHEN** 用戶結帳且 Redis `DECRBY stock:{product_id} quantity` 回傳值 < 0
- **THEN** 系統 **MUST** 立即執行 `INCRBY stock:{product_id} quantity` 回滾
- **AND** 回傳 HTTP 400 庫存不足錯誤，不進入 DB 事務

#### Scenario: 多商品購物車部分預扣失敗
- **WHEN** 購物車包含多個商品且其中一個商品 Redis 預扣失敗
- **THEN** 系統 **MUST** 回滾所有已成功預扣的商品庫存（`INCRBY`）
- **AND** 回傳 HTTP 400 庫存不足錯誤，指明哪個商品庫存不足

### Requirement: Redis 庫存預扣失敗回滾
系統 **SHALL** 在 DB 事務失敗時回滾 Redis 預扣的庫存，確保 Redis 庫存不會無故減少。

#### Scenario: DB 事務失敗後回滾 Redis 庫存
- **WHEN** Redis 預扣成功但後續 DB 事務（建立訂單、扣減 DB 庫存）失敗
- **THEN** 系統 **MUST** 對所有已預扣的商品執行 `INCRBY stock:{product_id} quantity` 回滾

### Requirement: Redis 庫存初始化與同步
系統 **SHALL** 在商品建立與庫存調整時同步更新 Redis 庫存，確保 Redis 庫存資料可用。

#### Scenario: 商品建立時初始化 Redis 庫存
- **WHEN** Admin 建立新商品且設定庫存數量
- **THEN** 系統 **MUST** 執行 `SET stock:{product_id} quantity` 將庫存寫入 Redis

#### Scenario: Admin 調整庫存時同步 Redis
- **WHEN** Admin 透過 API 調整商品庫存
- **THEN** 系統 **MUST** 同步更新 Redis 庫存值（`INCRBY stock:{product_id} delta`）

#### Scenario: Redis key 不存在時自動初始化
- **WHEN** 結帳預扣時發現 `stock:{product_id}` key 不存在於 Redis
- **THEN** 系統 **MUST** 從 DB 讀取當前庫存並寫入 Redis（`SET stock:{product_id} quantity`），然後重新執行預扣

### Requirement: StockRedisService 封裝
系統 **SHALL** 提供統一的 `StockRedisService` class 封裝所有 Redis 庫存操作。

#### Scenario: 提供標準化庫存操作介面
- **WHEN** 任何 use case 需要操作 Redis 庫存
- **THEN** **MUST** 透過 `StockRedisService` 的方法（`init_stock`、`try_deduct`、`rollback`、`get_stock`）操作，不直接呼叫 Redis client
