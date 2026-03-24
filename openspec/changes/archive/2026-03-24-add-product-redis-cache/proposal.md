## Why

目前每次用戶瀏覽商品列表或商品詳情頁時，都會直接查詢 PostgreSQL 資料庫。商品資訊屬於讀多寫少的資料，適合透過 Redis 快取來降低資料庫負擔、提升回應速度，尤其在高流量情境下效果更明顯。

## What Changes

- 新增 `ProductCacheService`，負責商品列表與商品詳情的 Redis 快取讀寫與失效
- 在商品列表（`GET /api/v1/products`）與商品詳情（`GET /api/v1/products/{id}`）的查詢流程中加入快取層：cache hit 直接回傳，cache miss 查詢資料庫後寫入快取
- **快取更新策略（Cache-Aside + Write-Invalidate）**：
  - **讀取路徑**：先查 Redis，cache miss 時查 DB 並回寫快取（Cache-Aside pattern）
  - **寫入路徑**：管理員新增、修改、刪除商品時，主動刪除（invalidate）對應的快取 key，而非更新快取內容。下一次讀取時會自動從 DB 重建快取
  - **關鍵更新時間點**：
    1. `CreateProductUseCase` 完成後 → 刪除所有商品列表快取（新商品需出現在列表中）
    2. `UpdateProductUseCase` 完成後 → 刪除該商品詳情快取 + 所有商品列表快取
    3. `DeleteProductUseCase` 完成後 → 刪除該商品詳情快取 + 所有商品列表快取
    4. `ToggleProductActiveUseCase` 完成後 → 刪除該商品詳情快取 + 所有商品列表快取
    5. `AdjustProductStockUseCase` 完成後 → 刪除該商品詳情快取（庫存變動需即時反映）
- 為快取設定 TTL（商品詳情 30 分鐘、商品列表 10 分鐘），作為最後防線確保資料最終一致性

## Capabilities

### New Capabilities
- `product-cache`: 商品資訊 Redis 快取機制，涵蓋 Cache-Aside 讀取策略、Write-Invalidate 寫入失效策略、TTL 過期保護、以及各操作時間點的快取清除邏輯

### Modified Capabilities

（無需修改現有 spec 層級的行為需求）

## Impact

- **後端程式碼**：新增 `ProductCacheService`（位於 `infrastructure/`），修改 product 模組的 use case 與 route handler 以注入快取服務
- **Redis**：新增 `product:detail:{id}` 與 `product:list:{hash}` 等 key pattern，增加記憶體用量
- **API 行為**：對外 API 介面不變，但回應速度提升；快取 TTL 過期前的短暫資料不一致為可接受的 trade-off
- **依賴**：無新增外部依賴，沿用現有的 `redis.asyncio` 與 `get_redis()` 基礎設施
