## ADDED Requirements

### Requirement: 商品詳情快取讀取
系統 SHALL 在查詢單一商品詳情時，先從 Redis 快取讀取。若快取命中（cache hit），SHALL 直接回傳快取資料而不查詢資料庫。若快取未命中（cache miss），SHALL 查詢資料庫並將結果寫入 Redis 快取。

#### Scenario: 快取命中時回傳快取資料
- **WHEN** 用戶請求 `GET /api/v1/products/{product_id}` 且 Redis 中存在 `product:detail:{product_id}` key
- **THEN** 系統直接從 Redis 回傳商品資料，不查詢 PostgreSQL

#### Scenario: 快取未命中時查詢資料庫並回寫快取
- **WHEN** 用戶請求 `GET /api/v1/products/{product_id}` 且 Redis 中不存在對應 key
- **THEN** 系統查詢 PostgreSQL 取得商品資料，將結果以 JSON 格式寫入 Redis（key: `product:detail:{product_id}`，TTL: 30 分鐘），並回傳資料

### Requirement: 商品列表快取讀取
系統 SHALL 在查詢商品列表時，根據查詢參數組合先從 Redis 快取讀取。快取 key 由查詢參數（skip, limit, category_id, category_ids, is_active）的 hash 值組成。

#### Scenario: 列表快取命中
- **WHEN** 用戶請求 `GET /api/v1/products` 且相同查詢參數組合的快取存在於 Redis
- **THEN** 系統直接從 Redis 回傳商品列表資料，不查詢 PostgreSQL

#### Scenario: 列表快取未命中
- **WHEN** 用戶請求 `GET /api/v1/products` 且對應查詢參數的快取不存在
- **THEN** 系統查詢 PostgreSQL 取得商品列表，將結果寫入 Redis（key: `product:list:{params_hash}`，TTL: 10 分鐘），並回傳資料

### Requirement: 商品新增時快取失效
系統 SHALL 在管理員成功新增商品後，刪除所有商品列表快取，使下次列表查詢從資料庫重新載入。

#### Scenario: 新增商品後列表快取被清除
- **WHEN** 管理員成功新增一筆商品
- **THEN** 系統使用 SCAN 指令刪除所有 `product:list:*` pattern 的 Redis key

### Requirement: 商品更新時快取失效
系統 SHALL 在管理員成功更新商品後，刪除該商品的詳情快取以及所有商品列表快取。

#### Scenario: 更新商品後相關快取被清除
- **WHEN** 管理員成功更新商品 `{product_id}` 的資料
- **THEN** 系統刪除 `product:detail:{product_id}` key 以及所有 `product:list:*` pattern 的 key

### Requirement: 商品刪除時快取失效
系統 SHALL 在管理員成功刪除商品後，刪除該商品的詳情快取以及所有商品列表快取。

#### Scenario: 刪除商品後相關快取被清除
- **WHEN** 管理員成功刪除商品 `{product_id}`
- **THEN** 系統刪除 `product:detail:{product_id}` key 以及所有 `product:list:*` pattern 的 key

### Requirement: 商品上下架時快取失效
系統 SHALL 在管理員切換商品上下架狀態後，刪除該商品的詳情快取以及所有商品列表快取。

#### Scenario: 切換上下架後相關快取被清除
- **WHEN** 管理員對商品 `{product_id}` 執行 toggle-active 操作
- **THEN** 系統刪除 `product:detail:{product_id}` key 以及所有 `product:list:*` pattern 的 key

### Requirement: 庫存調整時快取失效
系統 SHALL 在管理員調整商品庫存後，刪除該商品的詳情快取。

#### Scenario: 調整庫存後詳情快取被清除
- **WHEN** 管理員對商品 `{product_id}` 執行庫存調整
- **THEN** 系統刪除 `product:detail:{product_id}` key

### Requirement: Redis 不可用時降級為直接查詢
系統 SHALL 在 Redis 連線失敗或操作異常時，降級為直接查詢 PostgreSQL，不影響 API 正常回應。

#### Scenario: Redis 連線失敗時 fallback 到資料庫
- **WHEN** 用戶請求商品資料但 Redis 連線異常
- **THEN** 系統捕獲 Redis 異常，直接查詢 PostgreSQL 回傳資料，API 回應正常（不回傳錯誤）

#### Scenario: 快取寫入失敗不影響回應
- **WHEN** 系統從 PostgreSQL 查詢到商品資料後，寫入 Redis 快取時發生異常
- **THEN** 系統仍正常回傳商品資料給用戶，僅記錄 warning log
