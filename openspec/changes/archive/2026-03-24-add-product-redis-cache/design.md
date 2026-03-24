## Context

目前商品模組的所有讀取操作（列表、詳情）都直接查詢 PostgreSQL。Redis 在專案中已有使用：`StockRedisService` 管理庫存防超賣、`HybridCartRepository` 管理購物車。現有基礎設施（`get_redis()`、連線池、config）已完備，無需額外建置。

商品資料特性：讀多寫少、更新頻率低（僅管理員操作）、資料量可控（商品數量有限），非常適合 Cache-Aside 模式。

## Goals / Non-Goals

**Goals:**
- 降低商品列表與詳情頁的 PostgreSQL 查詢頻率
- 對使用者端 API 回應速度有可感知的提升
- 管理員操作後，快取能即時失效，確保資料一致性
- 沿用現有 Redis 基礎設施與專案 Clean Architecture 慣例

**Non-Goals:**
- 不實作前端層的快取（HTTP Cache-Control header 等）
- 不實作分類（Category）的獨立快取
- 不實作 Redis Pub/Sub 或多節點快取同步（目前為單 Redis 節點架構）
- 不修改管理員端列表查詢的快取（admin list 有搜尋、排序等複雜查詢，暫不納入）

## Decisions

### 1. 快取策略：Cache-Aside + Write-Invalidate

**選擇**：讀取時使用 Cache-Aside（lazy loading），寫入時使用 Invalidate（刪除快取）而非 Write-Through（更新快取）。

**替代方案**：
- Write-Through（寫入時同步更新快取）：實作較複雜，需將 domain entity 序列化後寫入，且在 use case 中需處理快取寫入失敗的情境
- Read-Through（由快取層代理 DB 讀取）：需要額外的快取代理層，過度設計

**理由**：Write-Invalidate 更簡單可靠——刪除一個 key 不會失敗（即使 key 不存在也不報錯），且避免快取與 DB 資料不一致的風險。下次讀取自動重建快取。

### 2. 快取層放置位置：Use Case 層

**選擇**：在 application use case 層注入 `ProductCacheService`，由 use case 決定何時讀取/失效快取。

**替代方案**：
- Repository 層裝飾器：透明但難以控制列表快取的 key 組合，且 repository 不應知道快取邏輯
- Route handler 層：違反 Clean Architecture，商業邏輯外洩到 presentation 層

**理由**：與現有 `StockRedisService` 在 use case 注入的模式一致，保持架構一致性。

### 3. 快取 Key 設計

- 商品詳情：`product:detail:{product_id}` — 以 UUID 為 key，一對一映射
- 商品列表：`product:list:{params_hash}` — 將查詢參數（skip, limit, category_id, category_ids, is_active）排序後做 SHA256 hash 作為 key
- 使用 `product:list:*` pattern 做批次刪除（列表快取失效時）

**替代方案**：
- 列表快取用固定 key + 版本號：需額外維護版本計數器，增加複雜度
- 不快取列表只快取詳情：列表查詢通常比詳情更耗資源（JOIN、分頁），放棄列表快取效益損失大

### 4. TTL 設定

- 商品詳情：30 分鐘
- 商品列表：10 分鐘（列表涉及排序和分頁，資料組合多，較短 TTL 減少過時資料）

### 5. 序列化格式：JSON

使用 `json.dumps/loads` 搭配 Pydantic DTO 的 `model_dump/model_validate`。JSON 足夠快、可讀性好、除錯方便，且 Pydantic v2 原生支援。無需額外依賴。

## Risks / Trade-offs

- **短暫資料不一致** → TTL 過期後自動修正；管理員操作會主動 invalidate，實務上不一致窗口極短
- **Redis 連線中斷時的降級** → 快取服務的所有操作需 try/except，Redis 不可用時 fallback 到直接查詢 DB，確保服務不中斷
- **`KEYS product:list:*` 在大量 key 時效能差** → 使用 `SCAN` 指令替代 `KEYS` 進行 pattern 匹配刪除，避免阻塞 Redis
- **記憶體用量增加** → 商品數量有限（百級到千級），JSON 序列化後單筆約 1-3 KB，整體記憶體影響可忽略
