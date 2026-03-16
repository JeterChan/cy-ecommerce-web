from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from uuid import UUID

@dataclass
class ProductImage:
    """商品圖片領域實體"""
    url: str
    alt_text: Optional[str] = None
    is_primary: bool = False
    id: Optional[UUID] = None

@dataclass
class Product:
    """商品領域實體"""
    name: str
    description: Optional[str]
    price: Decimal
    stock_quantity: int
    id: Optional[UUID] = None
    is_active: bool = True
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    images: List[ProductImage] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def validate(self) -> None:
        """驗證商品資料的業務規則"""
        errors = []

        # 1. 名稱驗證
        if not self.name or not self.name.strip():
            errors.append("商品名稱不可為空")
        elif len(self.name) > 100:
            errors.append("商品名稱不可超過 100 字元")

        # 2. 價格驗證
        if self.price <= 0:
            errors.append("商品價格必須大於 0")

        # 3. 庫存驗證
        if self.stock_quantity < 0:
            errors.append("庫存數量不可為負數")

        # 4. 描述長度驗證
        if self.description and len(self.description) > 1000:
            errors.append("商品描述不可超過 1000 字元")

        # 5. 圖片驗證
        if len(self.images) > 5:
            errors.append("每個商品最多只能有 5 張圖片")
        
        if self.images:
            primary_count = sum(1 for img in self.images if img.is_primary)
            if primary_count == 0:
                errors.append("商品必須至少設定一張主圖")
            elif primary_count > 1:
                errors.append("商品只能有一張主圖")

        if errors:
            raise ValueError(f"商品資料驗證失敗: {', '.join(errors)}")

    def deactivate(self) -> None:
        """下架商品"""
        self.is_active = False

    def activate(self) -> None:
        """上架商品"""
        self.is_active = True

    def update_stock(self, quantity_change: int) -> None:
        new_quantity = self.stock_quantity + quantity_change
        if new_quantity < 0:
            raise ValueError(f"庫存不足，無法減少 {abs(quantity_change)} 件")
        self.stock_quantity = new_quantity

@dataclass
class Category:
    id: Optional[int]
    name: str
    slug: str

    def validate(self) -> None:
        """驗證分類資料的業務規則"""
        errors = []

        if not self.name or not self.name.strip():
            errors.append("分類名稱不可為空")

        if not self.slug or not self.slug.strip():
            errors.append("分類 slug 不可為空")
        elif not self.slug.islower() or ' ' in self.slug:
            errors.append("分類 slug 必須是小寫且不含空格")

        if errors:
            raise ValueError(f"分類資料驗證失敗: {', '.join(errors)}")
