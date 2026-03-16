# Research: Member Cart Async Sync (Celery Implementation)

## Decisions

### 1. Integration with Celery
- **Decision**: 使用 Celery 處理非同步同步任務。
- **Broker**: Redis (使用專案現有 Redis 配置)。
- **Task Definition**: 定義一個 `sync_member_cart_task`，接收 `user_id` 作為參數。
- **Hybrid Repository**: 實作 `HybridCartRepository` 作為協調者 (Orchestrator)。它滿足 `ICartRepository` 介面，負責優先寫入 Redis 並分發非同步任務，同時處理讀取時的快取回退 (Read Fallback)。
- **Rationale**: 利用現有的 Celery 依賴，減少開發成本並獲得開箱即用的重試與錯誤管理機制。

### 2. Consistency Strategy
- **Decision**: **Cache-Aside + Async Write-Behind**。
- **Flow**:
  1. API 接收到請求後，立即更新 **Redis Hash** (`cart:{user_id}`)。
  2. 呼叫 `sync_member_cart_task.delay(user_id)`。
  3. API 立即回傳 `201/200` 給前端。
  4. Celery Worker 執行任務：讀取 Redis Hash 狀態，並全量或增量同步至 PostgreSQL `cart_items` 表。
- **Rationale**: 確保使用者感受到極速響應，同時由背景穩定同步至持久層。

### 3. Idempotency & Conflict Resolution
- **Decision**: **基於狀態的 UPSERT 同步**。
- **Logic**: Celery 任務執行時，讀取 Redis 中該會員的完整購物車，並使用 PostgreSQL 的 `INSERT ... ON CONFLICT (user_id, product_id) DO UPDATE` 進行批量同步。對於 Redis 中已刪除但 DB 仍存在的項目，則執行刪除操作。
- **Concurrency**: 透過 Redis 分散式鎖 (`lock:cart_sync:{user_id}`) 確保**單一會員**的同步任務串行化執行。
- **Rationale**: UPSERT 避免了「先刪後加」過程中的短暫數據真空，並確保了事務的原子性。

### 4. Failure Handling
- **Decision**: **Exponential Backoff Retry**。
- **Logic**: 若資料庫斷線，Celery 將自動進行指數退避重試（3-5 次）。若最終失敗，將進入 Celery 的失敗處理流程或記錄到專用的日誌表。
- **Rationale**: 符合規格書中 Q1: A 的要求。

## Alternatives Considered

### Alternative: Pure Redis Stream Consumer
- **Rejected Because**: 雖然輕量，但需要手動實作重試、監控與 Worker 進程守護，相較於專案現有的 Celery，開發複雜度較高。
