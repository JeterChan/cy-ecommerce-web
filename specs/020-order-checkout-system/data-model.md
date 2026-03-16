# Data Model: Order Checkout and Management System

## 實體定義 (Entities)

### 1. Order (訂單表)
- **ID**: UUID (Primary Key)
- **UserID**: UUID (Foreign Key to Users)
- **Status**: Enum (PROCESSING, SHIPPED, COMPLETED, CANCELLED)
- **TotalAmount**: Decimal (12, 2)
- **RecipientName**: String (255)
- **RecipientPhone**: String (20)
- **ShippingAddress**: Text
- **PaymentMethod**: String (e.g., "COD")
- **CreatedAt**: DateTime (Index)
- **UpdatedAt**: DateTime

### 2. OrderItem (訂單明細表)
- **ID**: UUID (Primary Key)
- **OrderID**: UUID (Foreign Key to Orders, Index)
- **ProductID**: UUID (Foreign Key to Products)
- **Price**: Decimal (12, 2) (快照結帳時的價格)
- **Quantity**: Integer

## 狀態轉換與業務規則

### 訂單生命週期 (Lifecycle)
- **PROCESSING**: 訂單剛建立，待庫存與付款處理。
- **SHIPPED**: 訂單已發貨。
- **COMPLETED**: 訂單已完成收貨。
- **CANCELLED**: 訂單已取消。

### 事務邏輯規則
1. **庫存鎖定**: 使用 `FOR UPDATE` 鎖定 `products` 表中的相關行。
2. **防超賣**: `UPDATE products SET stock_quantity = stock_quantity - :qty WHERE id = :id AND stock_quantity >= :qty`。
3. **價格快照**: `order_items.price` 必須使用 `products.price` 的最新快照。

## 關聯性
- 一個 **Order** 包含多個 **OrderItem** (1:N)。
- 一個 **User** 擁有多個 **Order** (1:N)。
- 一個 **Product** 出現在多個 **OrderItem** 中 (N:M via OrderItem)。
