"""
Order Module - Domain Entities

此檔案定義訂單相關的領域實體。
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, List, Union
from datetime import datetime
from uuid import UUID


@dataclass
class OrderItem:
    """訂單項目領域實體"""
    product_id: UUID  # 使用 UUID 格式與 Product 表一致
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    id: Optional[UUID] = None
    order_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def validate(self) -> None:
        """驗證訂單項目資料的業務規則"""
        errors = []

        if self.quantity <= 0:
            errors.append("商品數量必須大於 0")

        if self.unit_price < 0:
            errors.append("商品單價不可為負數")

        expected_subtotal = self.unit_price * self.quantity
        if self.subtotal != expected_subtotal:
            errors.append(f"小計金額不正確，預期 {expected_subtotal}，實際 {self.subtotal}")

        if errors:
            raise ValueError(f"訂單項目資料驗證失敗: {', '.join(errors)}")


@dataclass
class Order:
    """訂單領域實體"""
    user_id: UUID  # Changed to UUID to match database
    order_number: str
    total_amount: Decimal
    shipping_fee: Decimal
    status: str  # OrderStatus enum value
    recipient_name: str
    recipient_phone: str
    shipping_address: str
    payment_method: str
    items: List[OrderItem] = field(default_factory=list)
    id: Optional[UUID] = None
    note: Optional[str] = None
    admin_note: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status_updated_at: Optional[datetime] = None

    def validate(self) -> None:
        """驗證訂單資料的業務規則"""
        errors = []

        # user_id validation removed as UUID is not a string to strip()

        if self.total_amount < 0:
            errors.append("訂單總金額不可為負數")

        if self.shipping_fee < 0:
            errors.append("運費不可為負數")

        if not self.items:
            errors.append("訂單必須至少包含一個商品項目")

        if self.note and len(self.note) > 500:
            errors.append("訂單備註不可超過 500 字元")
        
        if self.admin_note and len(self.admin_note) > 1000:
            errors.append("管理員備註不可超過 1000 字元")
        
        if not self.recipient_name or not self.recipient_name.strip():
            errors.append("收件人姓名不可為空")
            
        if not self.recipient_phone or not self.recipient_phone.strip():
            errors.append("收件人電話不可為空")
            
        if not self.shipping_address or not self.shipping_address.strip():
            errors.append("收件地址不可為空")

        # 驗證總金額是否等於各項目小計加運費
        items_total = sum(item.subtotal for item in self.items)
        expected_total = items_total + self.shipping_fee
        if self.total_amount != expected_total:
            errors.append(f"訂單總金額不正確，預期 {expected_total}，實際 {self.total_amount}")

        # 驗證每個訂單項目
        for idx, item in enumerate(self.items):
            try:
                item.validate()
            except ValueError as e:
                errors.append(f"訂單項目 {idx + 1}: {str(e)}")

        if errors:
            raise ValueError(f"訂單資料驗證失敗: {', '.join(errors)}")

    def calculate_total(self) -> Decimal:
        """計算訂單總金額"""
        items_total = sum(item.subtotal for item in self.items)
        return items_total + self.shipping_fee
