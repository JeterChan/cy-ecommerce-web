from pydantic import BaseModel, Field, ConfigDict, field_validator
from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class ProductResponseDTO(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int
    is_active: bool
    image_url: Optional[str] = None
    category_ids: List[int] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

    @field_validator('category_ids', mode='before')
    @classmethod
    def extract_category_ids(cls, v, info):
        if hasattr(v, '__iter__') and not isinstance(v, (str, bytes)):
            return [cat.id for cat in v if hasattr(cat, 'id')]
        return v or []
