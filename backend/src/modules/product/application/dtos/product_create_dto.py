from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from typing import Optional, List

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    stock_quantity: int = Field(..., ge=0)
    is_active: bool = Field(default=True)
    image_url: Optional[str] = Field(None, max_length=255)
    category_ids: Optional[List[int]] = Field(default_factory=list)

class ProductCreateDTO(ProductBase):
    model_config = ConfigDict(json_schema_extra={"example": {"name": "iPhone 15 Pro Max", "description": "...", "price": 39900.00, "stock_quantity": 50, "is_active": True, "image_url": "https://example.com/img.jpg", "category_ids": [1, 2]}})
