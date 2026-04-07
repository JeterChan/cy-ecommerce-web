from pydantic import BaseModel, Field, ConfigDict, computed_field
from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ProductImageDTO(BaseModel):
    id: Optional[UUID] = None
    url: str
    alt_text: Optional[str] = None
    is_primary: bool = False
    model_config = ConfigDict(from_attributes=True)


class ProductResponseDTO(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int
    is_active: bool
    images: List[ProductImageDTO] = Field(default_factory=list)
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def category_ids(self) -> List[int]:
        """相容性欄位：回傳單一分類 ID 的列表"""
        return [self.category_id] if self.category_id else []

    @computed_field
    @property
    def category_names(self) -> List[str]:
        """相容性欄位：回傳單一分類名稱的列表"""
        return [self.category_name] if self.category_name else []

    @computed_field
    @property
    def is_low_stock(self) -> bool:
        """即時計算庫存緊張狀態"""
        return 0 < self.stock_quantity < 5

    # extract_category_ids validator removed

    @computed_field
    @property
    def image_url(self) -> Optional[str]:
        """相容性欄位：回傳主圖 URL"""
        for img in self.images:
            if img.is_primary:
                return img.url
        return self.images[0].url if self.images else None


class ProductListResponseDTO(BaseModel):
    items: List[ProductResponseDTO]
    total: int
    skip: int
    limit: int
    model_config = ConfigDict(from_attributes=True)
