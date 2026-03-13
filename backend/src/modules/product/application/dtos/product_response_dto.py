from pydantic import BaseModel, Field, ConfigDict, field_validator, computed_field
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
    category_ids: List[int] = Field(default_factory=list)
    category_names: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def is_low_stock(self) -> bool:
        """即時計算庫存緊張狀態"""
        return 0 < self.stock_quantity < 5

    @field_validator('category_ids', mode='before')
    @classmethod
    def extract_category_ids(cls, v, info):
        if not v:
            return []
        if hasattr(v, '__iter__') and not isinstance(v, (str, bytes)):
            result = []
            for cat in v:
                if isinstance(cat, int):
                    result.append(cat)
                elif hasattr(cat, 'id'):
                    result.append(cat.id)
            return result
        return []

    @computed_field
    @property
    def image_url(self) -> Optional[str]:
        """相容性欄位：回傳主圖 URL"""
        for img in self.images:
            if img.is_primary:
                return img.url
        return self.images[0].url if self.images else None

