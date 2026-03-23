## 1. 準備工作

- [ ] 1.1 建立新 branch `feat/add-backend-unit-tests`
- [ ] 1.2 建立測試目錄結構：`tests/unit/modules/{product,cart,order}/` 及 `tests/unit/infrastructure/`，每個目錄加入 `__init__.py`

## 2. Product 模組單元測試

- [ ] 2.1 建立 `tests/unit/modules/product/test_entities.py`：Product.validate() 所有分支（name、price、stock、description、images、primary image）、update_stock() 成功與失敗、Category.validate()
- [ ] 2.2 建立 `tests/unit/modules/product/test_use_cases.py`：CreateProductUseCase（成功建立 + Redis init）、AdjustProductStockUseCase（成功調整 + Redis sync、庫存不足）

## 3. Cart 模組單元測試

- [ ] 3.1 建立 `tests/unit/modules/cart/test_use_cases.py`：AddToCartUseCase（成功加入、累加超出庫存）、UpdateCartItemQuantityUseCase（超出庫存）
- [ ] 3.2 建立 `tests/unit/modules/cart/test_merge_service.py`：MergeCartUseCase（累加邏輯、新增邏輯）、CartMergeService 基本流程

## 4. Order 模組單元測試

- [ ] 4.1 建立 `tests/unit/modules/order/test_entities.py`：OrderItem.validate()（quantity、subtotal 算術）、Order.validate()（空 items、total 交叉驗證）、Order.calculate_total()
- [ ] 4.2 建立 `tests/unit/modules/order/test_use_cases.py`：CheckoutUseCase（空購物車、Redis 預扣回滾、訂單編號格式）、UpdateOrderStatusUseCase（非擁有者拒絕、取消訂單恢復庫存）

## 5. StockRedisService 單元測試

- [ ] 5.1 建立 `tests/unit/infrastructure/test_stock_redis_service.py`：try_deduct（庫存充足、庫存不足回滾、lazy init 重試、lazy init 後仍不足）、rollback、sync_stock（key 存在 delta 調整、key 不存在從 DB 載入）

## 6. Auth 模組補強測試

- [ ] 6.1 補強 `tests/unit/modules/auth/test_use_cases.py`：DeleteAccountUseCase（成功刪除含 email 前綴、密碼錯誤）、UpdateProfileUseCase（部分更新、username 重複）

## 7. 驗證

- [ ] 7.1 執行 `pytest tests/unit/ -v` 確認所有新增單元測試通過
