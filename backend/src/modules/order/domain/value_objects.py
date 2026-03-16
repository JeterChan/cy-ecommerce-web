"""
Order Module - Value Objects

此檔案定義訂單相關的值物件（不可變物件）。
"""

from enum import Enum


class OrderStatus(str, Enum):
    """訂單狀態枚舉"""
    PENDING = "PENDING"           # 待處理（訂單已建立，待付款）
    PAID = "PAID"                 # 已付款
    SHIPPED = "SHIPPED"           # 已出貨
    COMPLETED = "COMPLETED"       # 已完成
    CANCELLED = "CANCELLED"       # 已取消
    REFUNDED = "REFUNDED"         # 已退款

    def __str__(self) -> str:
        return self.value


class PaymentMethod(str, Enum):
    """付款方式枚舉"""
    COD = "COD"                       # 貨到付款
    BANK_TRANSFER = "BANK_TRANSFER"   # 銀行轉帳

    def __str__(self) -> str:
        return self.value

