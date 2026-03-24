## ADDED Requirements

### Requirement: Product domain entity 單元測試
系統 SHALL 提供 `Product` entity 的單元測試，涵蓋所有 `validate()` 分支與 `update_stock()` 邏輯。

#### Scenario: Product 名稱驗證
- **WHEN** 建立 `Product` 並呼叫 `validate()`，name 為空字串或超過 100 字元
- **THEN** MUST 拋出 `ValueError`

#### Scenario: Product 價格驗證
- **WHEN** 建立 `Product` 並呼叫 `validate()`，price <= 0
- **THEN** MUST 拋出 `ValueError`

#### Scenario: Product 庫存驗證
- **WHEN** 建立 `Product` 並呼叫 `validate()`，stock_quantity < 0
- **THEN** MUST 拋出 `ValueError`

#### Scenario: Product 描述長度驗證
- **WHEN** 建立 `Product` 並呼叫 `validate()`，description 超過 1000 字元
- **THEN** MUST 拋出 `ValueError`

#### Scenario: Product 圖片數量驗證
- **WHEN** 建立 `Product` 並呼叫 `validate()`，images 超過 5 張
- **THEN** MUST 拋出 `ValueError`

#### Scenario: Product 主圖驗證
- **WHEN** 建立 `Product` 並呼叫 `validate()`，is_primary 為 True 的圖片數量不等於 1
- **THEN** MUST 拋出 `ValueError`

#### Scenario: Product 合法資料通過驗證
- **WHEN** 建立合法的 `Product` 並呼叫 `validate()`
- **THEN** MUST 不拋出任何例外

#### Scenario: Product 庫存更新成功
- **WHEN** 呼叫 `update_stock(delta)` 且結果 >= 0
- **THEN** MUST 更新 `stock_quantity` 為新值

#### Scenario: Product 庫存更新失敗
- **WHEN** 呼叫 `update_stock(delta)` 且結果 < 0
- **THEN** MUST 拋出 `ValueError`

### Requirement: Category domain entity 單元測試
系統 SHALL 提供 `Category` entity 的單元測試，涵蓋 `validate()` 邏輯。

#### Scenario: Category slug 格式驗證
- **WHEN** 建立 `Category` 並呼叫 `validate()`，slug 包含大寫或空格
- **THEN** MUST 拋出 `ValueError`

#### Scenario: Category 合法資料通過驗證
- **WHEN** 建立合法的 `Category` 並呼叫 `validate()`
- **THEN** MUST 不拋出任何例外

### Requirement: Order domain entity 單元測試
系統 SHALL 提供 `Order` 和 `OrderItem` entity 的單元測試。

#### Scenario: OrderItem 數量驗證
- **WHEN** 建立 `OrderItem` 並呼叫 `validate()`，quantity <= 0
- **THEN** MUST 拋出 `ValueError`

#### Scenario: OrderItem subtotal 算術驗證
- **WHEN** 建立 `OrderItem` 並呼叫 `validate()`，subtotal != unit_price * quantity
- **THEN** MUST 拋出 `ValueError`

#### Scenario: OrderItem 合法資料通過驗證
- **WHEN** 建立合法的 `OrderItem` 並呼叫 `validate()`
- **THEN** MUST 不拋出任何例外

#### Scenario: Order items 不可為空
- **WHEN** 建立 `Order` 並呼叫 `validate()`，items 為空列表
- **THEN** MUST 拋出 `ValueError`

#### Scenario: Order total 交叉驗證
- **WHEN** 建立 `Order` 並呼叫 `validate()`，total_amount != sum(items.subtotal) + shipping_fee
- **THEN** MUST 拋出 `ValueError`

#### Scenario: Order 合法資料通過驗證
- **WHEN** 建立合法的 `Order` 並呼叫 `validate()`
- **THEN** MUST 不拋出任何例外

#### Scenario: Order calculate_total 計算正確
- **WHEN** 呼叫 `calculate_total()`
- **THEN** MUST 回傳 sum(items.subtotal) + shipping_fee

### Requirement: Product use case 單元測試
系統 SHALL 提供 `CreateProductUseCase` 和 `AdjustProductStockUseCase` 的單元測試，使用 mock repository。

#### Scenario: CreateProductUseCase 成功建立商品並初始化 Redis 庫存
- **WHEN** 傳入合法商品資料呼叫 `execute()`
- **THEN** MUST 呼叫 `product_repo.create()` 並呼叫 `StockRedisService.init_stock()`

#### Scenario: AdjustProductStockUseCase 成功調整庫存並同步 Redis
- **WHEN** 傳入合法 delta 呼叫 `execute()`
- **THEN** MUST 呼叫 `product.update_stock(delta)` 並呼叫 `StockRedisService.sync_stock()`

#### Scenario: AdjustProductStockUseCase 庫存不足時拋出例外
- **WHEN** delta 導致庫存 < 0
- **THEN** MUST 拋出 `ValueError`，不呼叫 `sync_stock()`

### Requirement: Cart use case 單元測試
系統 SHALL 提供購物車相關 use case 的單元測試。

#### Scenario: AddToCartUseCase 庫存充足時成功加入
- **WHEN** 商品庫存充足且呼叫 `execute()`
- **THEN** MUST 呼叫 `repository.add_item()`

#### Scenario: AddToCartUseCase 累加後超出庫存時拋出例外
- **WHEN** 現有數量 + 新增數量 > 商品庫存
- **THEN** MUST 拋出 `InsufficientStockException`

#### Scenario: UpdateCartItemQuantityUseCase 超出庫存時拋出例外
- **WHEN** 指定數量 > 商品庫存
- **THEN** MUST 拋出 `InsufficientStockException`

#### Scenario: MergeCartUseCase 合併邏輯
- **WHEN** guest 購物車有商品且 user 購物車已有相同商品
- **THEN** MUST 累加數量而非覆蓋

#### Scenario: MergeCartUseCase 新增邏輯
- **WHEN** guest 購物車有商品且 user 購物車沒有該商品
- **THEN** MUST 新增該商品至 user 購物車

### Requirement: Order use case 單元測試
系統 SHALL 提供結帳與訂單狀態更新相關 use case 的單元測試。

#### Scenario: CheckoutUseCase 空購物車時拋出例外
- **WHEN** 購物車為空呼叫 `execute()`
- **THEN** MUST 拋出 `EmptyCartException`

#### Scenario: CheckoutUseCase Redis 預扣部分失敗時回滾已預扣庫存
- **WHEN** 多商品預扣中某一商品失敗
- **THEN** MUST 對所有已成功預扣的商品呼叫 `StockRedisService.rollback()`

#### Scenario: CheckoutUseCase 訂單編號格式正確
- **WHEN** 呼叫 `_generate_order_number()`
- **THEN** MUST 回傳 20 位純數字字串

#### Scenario: UpdateOrderStatusUseCase 非擁有者操作被拒絕
- **WHEN** `order.user_id != user_id` 呼叫 `execute()`
- **THEN** MUST 拋出例外

#### Scenario: UpdateOrderStatusUseCase 取消訂單時恢復庫存
- **WHEN** 狀態從 PENDING 變更為 CANCELLED
- **THEN** MUST 呼叫 `product_repo.atomic_adjust_stock()` 恢復每個商品的庫存

### Requirement: StockRedisService 單元測試
系統 SHALL 提供 `StockRedisService` 的完整單元測試，使用 mock Redis client。

#### Scenario: try_deduct 庫存充足時成功預扣
- **WHEN** `DECRBY` 回傳值 >= 0
- **THEN** MUST 回傳 `(True, remaining)`

#### Scenario: try_deduct 庫存不足時回滾並回傳失敗
- **WHEN** key 已存在且 `DECRBY` 回傳值 < 0
- **THEN** MUST 呼叫 `INCRBY` 回滾並回傳 `(False, 0)`

#### Scenario: try_deduct key 不存在時 lazy init 並重試
- **WHEN** key 不存在（`exists` 回傳 0）且 DB 有庫存資料
- **THEN** MUST 從 DB 載入庫存、`SET` key、重試 `DECRBY`

#### Scenario: try_deduct lazy init 後仍不足
- **WHEN** key 不存在，從 DB 載入後重試仍然不足
- **THEN** MUST 回滾並回傳 `(False, 0)`

#### Scenario: rollback 正確回滾
- **WHEN** 呼叫 `rollback(product_id, quantity)`
- **THEN** MUST 呼叫 `INCRBY stock:{product_id} quantity`

#### Scenario: sync_stock key 存在時 delta 調整
- **WHEN** key 存在且呼叫 `sync_stock(product_id, delta)`
- **THEN** MUST 呼叫 `INCRBY` 調整庫存

#### Scenario: sync_stock key 不存在時從 DB 載入
- **WHEN** key 不存在且呼叫 `sync_stock(product_id, delta)`
- **THEN** MUST 從 DB 載入庫存並 `SET` key

### Requirement: Auth use case 補強測試
系統 SHALL 補強 auth 模組現有單元測試的覆蓋缺口。

#### Scenario: DeleteAccountUseCase 成功刪除帳號
- **WHEN** 密碼驗證通過呼叫 `execute()`
- **THEN** MUST 設定 `is_active=False`、`deleted_at` 為當前時間、email 加上 `deleted_{id}_` 前綴

#### Scenario: DeleteAccountUseCase 密碼錯誤時拋出例外
- **WHEN** 密碼驗證失敗
- **THEN** MUST 拋出例外，不修改使用者資料

#### Scenario: UpdateProfileUseCase 部分更新
- **WHEN** 僅提供部分欄位（如只有 phone）
- **THEN** MUST 只更新提供的欄位，其餘保持不變

#### Scenario: UpdateProfileUseCase username 重複時拋出例外
- **WHEN** 新 username 已被其他使用者使用
- **THEN** MUST 拋出例外
