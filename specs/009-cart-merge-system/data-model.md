# 資料模型: 購物車合併系統

**功能**: 購物車合併系統
**最後更新**: 2026-01-25

## 概念實體

### Cart (購物車)
代表使用者 (訪客或會員) 所選購的商品集合。

- **訪客購物車 (Guest Cart)**: 暫時性，由 `guest_token` 識別。儲存於 Redis。
- **會員購物車 (Member Cart)**: 持久性，由 `user_id` 識別。儲存於 DB + Redis。

### Cart Item (購物車項目)
購物車內的特定商品及其數量。

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| product_id | UUID | 是 | 參照至商品 |
| quantity | Integer | 是 | 商品數量 (> 0) |
| added_at | Timestamp | 否 | 加入時間 (可選，用於排序) |

## 資料庫結構 (PostgreSQL)

**資料表**: `cart_items` (僅限會員)

| 欄位 | 類型 | 限制 | 說明 |
|------|------|------|------|
| id | UUID | PK | 紀錄唯一 ID |
| user_id | UUID | FK, Index | 購物車擁有者 |
| product_id | UUID | FK | 商品 |
| quantity | Integer | Check > 0 | 數量 |
| created_at | Timestamp | Default Now | |
| updated_at | Timestamp | Default Now | |

*註: 如果我們直接將項目連結至 `user_id`，則不一定需要 `carts` 表。然而，`carts` 表允許儲存購物車層級的中繼資料 (如優惠券等)。對於 MVP，將項目直接連結至 `user_id` 已足夠。*

## Redis 結構

**Key**: `cart:{owner_id}`
- `owner_id` 為 `user:{id}` 或 `guest:{token}`。

**Type**: Hash

| Field | Value | 說明 |
|-------|-------|------|
| `{product_id}` | `{quantity}` | 商品 ID 對應 數量 |

*範例*:
`HSET cart:guest:12345-abcde "prod-001" 2`