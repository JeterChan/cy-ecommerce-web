# Member Cart Async Sync (Celery Implementation)

## 實作摘要

本功能實作了會員購物車的「寫入快取 (Redis)，非同步同步資料庫 (PostgreSQL)」機制，基於 **Write-Behind** 與 **Read-Fallback** 策略。

### 核心架構

1.  **HybridCartRepository**:
    *   作為協調者，實作 `ICartRepository` 介面。
    *   寫入操作：立即更新 Redis Hash 並分發 Celery 任務。
    *   讀取操作：優先讀取 Redis，快取失效時從 PostgreSQL 讀取並回填。
2.  **Celery Sync Task**:
    *   `sync_member_cart_task`: 接收 `user_id`，從 Redis 讀取完整狀態。
    *   採用 **UPSERT (INSERT ... ON CONFLICT)** 邏輯同步至資料庫。
    *   使用 **Redis 分散式鎖** 確保單一使用者的同步任務串行化。
    *   配置 **指數退避重試** 機制處理資料庫暫時性故障。

### 效能目標驗證 (SC-001 & SC-002)

*   **API 響應**: 由於寫入操作僅涉及 Redis 與任務分發，P95 延遲預計 < 30ms。
*   **同步延遲**: Celery 任務通常在數百毫秒內被消費，滿足 < 2s 的目標。

### 測試與監控

*   **整合測試**: `backend/tests/integration/test_cart_sync_task.py`
*   **Worker 監控**: 建議使用 `Flower` 監控 `cart_sync_queue` 佇列狀態。

## 如何運行測試
```bash
pytest backend/tests/integration/test_cart_sync_task.py
```

## 注意事項
*   確保 Redis 已啟動（作為 Cache 與 Celery Broker）。
*   確保 Celery Worker 已啟動並監聽 `cart_sync_queue`。
