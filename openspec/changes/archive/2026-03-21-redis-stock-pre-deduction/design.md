## Context

目前結帳流程 (`CheckoutUseCase`) 使用 PostgreSQL `SELECT ... FOR UPDATE` 悲觀鎖保護庫存扣減。所有併發請求無論庫存是否充足，都必須進入 DB 排隊等待行鎖。壓力測試結果顯示 2000 VU 搶 10 個庫存時，p50 回應時間 2.5 秒，max 達 3.4 秒——其中 1990 個注定失敗的請求佔用了大量 DB 連線和鎖等待時間。

現有基礎設施已包含 Redis（用於購物車存儲），無需引入新依賴。

## Goals / Non-Goals

**Goals:**
- 透過 Redis 原子操作在 DB 層之前過濾掉庫存不足的請求，大幅降低失敗請求的回應時間
- 確保庫存不超賣（Redis 預扣 + DB 悲觀鎖雙重保障）
- Redis 與 DB 庫存在正常流程中保持最終一致性
- 對現有 API 介面零破壞性變更

**Non-Goals:**
- 不實作分散式鎖或 Lua 腳本——`DECRBY` 的原子性已足夠
- 不移除 DB 層悲觀鎖——保留作為最終一致性防線
- 不實作 Redis 庫存自動過期/重建機制——庫存是關鍵資料，由應用層主動管理
- 不處理 Redis 完全不可用的降級場景（MVP 階段，Redis 不可用則結帳失敗）

## Decisions

### 1. Redis Key 設計：`stock:{product_id}`

使用獨立的 key pattern `stock:{product_id}`，value 為整數庫存量。

- **為何不用 Hash**：每個商品只需存一個值，String type + `DECRBY` 最簡單且原子
- **為何不重用購物車的 key namespace**：職責分離，庫存與購物車是不同概念

### 2. 預扣流程：先 Redis DECRBY，失敗快速返回

```
checkout 請求
  │
  ▼
Redis DECRBY stock:{pid} quantity
  │
  ├─ 結果 >= 0 → 預扣成功，進入 DB 事務
  │                │
  │                ├─ DB 成功 → 完成
  │                └─ DB 失敗 → Redis INCRBY 回滾
  │
  └─ 結果 < 0  → Redis INCRBY 回滾，立即返回庫存不足
```

- **為何用 DECRBY 而非 GET + 判斷 + DECRBY**：DECRBY 本身是原子操作，回傳值即可判斷是否成功。GET 再 DECRBY 存在 TOCTOU 競態條件。
- **為何結果 < 0 需要 INCRBY 回滾**：DECRBY 會把值扣到負數，必須加回來維持正確的庫存計數。

### 3. 庫存同步點：商品建立、庫存調整、結帳成功

| 操作 | DB 動作 | Redis 動作 |
|------|---------|-----------|
| 商品建立 | INSERT product | `SET stock:{id} quantity` |
| Admin 調整庫存 | UPDATE stock_quantity | `INCRBY stock:{id} delta` |
| 結帳預扣 | — | `DECRBY stock:{id} quantity` |
| 結帳 DB 成功 | UPDATE stock_quantity (FOR UPDATE) | 不需操作（已預扣） |
| 結帳 DB 失敗 | ROLLBACK | `INCRBY stock:{id} quantity`（回滾） |

### 4. 多商品購物車處理：依序預扣，失敗全部回滾

購物車可能包含多個商品，每個需要獨立預扣。若任一商品預扣失敗，需回滾已成功的商品。

- **為何不用 Lua 腳本一次處理多個 key**：增加複雜度，且實際場景購物車商品數通常不多（1~5 個）

### 5. 新增 StockRedisService 統一管理

建立獨立 service class 封裝所有 Redis 庫存操作（init、decrby、incrby、get），避免 Redis 操作散落在各 use case 中。

## Risks / Trade-offs

- **Redis 與 DB 庫存不一致**：若應用崩潰在 DB commit 後、Redis 回滾前，Redis 庫存會偏高（少賣）。→ 緩解：可透過定期任務從 DB 同步庫存到 Redis，或在低頻操作（如 Admin 查看商品）時順便校正。MVP 階段「少賣」比「超賣」安全，可接受。
- **Redis 不可用導致結帳完全失敗**：→ 緩解：MVP 階段可接受。未來可加降級邏輯：Redis 不可用時 fallback 到純 DB 悲觀鎖流程。
- **Redis key 不存在（首次或被清除）**：`DECRBY` 對不存在的 key 會視為 0 再扣減，結果必然 < 0。→ 緩解：確保商品建立/更新時都同步初始化 Redis；若 key 不存在，在預扣前從 DB 讀取並初始化（lazy init）。
