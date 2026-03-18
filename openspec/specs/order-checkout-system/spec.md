# order-checkout-system Specification

## Purpose
TBD - created by archiving change admin-order-management. Update Purpose after archive.
## Requirements
### Requirement: 訂單狀態追蹤增強
訂單系統 **SHALL** 記錄每次狀態變更的關鍵時間點，以供後台分析與流程監控。

#### Scenario: 記錄狀態更新時間
- **WHEN** 訂單狀態從 `pending` 變更為任何其他狀態（如 `paid`, `shipped`, `cancelled`）
- **THEN** 系統 **MUST** 自動更新 `status_updated_at` 欄位為當前伺服器時間

### Requirement: 訂單狀態枚舉定義
系統 **SHALL** 定義一組標準化的訂單狀態枚舉，涵蓋從下單到售後的全週期。

#### Scenario: 支援完整的訂單狀態
- **WHEN** 系統讀取或寫入訂單狀態時
- **THEN** 狀態 **MUST** 僅限於：`pending`, `paid`, `shipped`, `delivered`, `completed`, `cancelled`, `refunding`, `refunded`

