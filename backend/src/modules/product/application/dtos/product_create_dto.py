from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from typing import Optional, List


class ProductImageCreateDTO(BaseModel):
    url: str
    alt_text: Optional[str] = None
    is_primary: bool = False


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    stock_quantity: int = Field(..., ge=0)
    is_active: bool = Field(default=True)
    images: List[ProductImageCreateDTO] = Field(default_factory=list)
    category_ids: Optional[List[int]] = Field(default_factory=list)


class ProductCreateDTO(ProductBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "iPhone 15 Pro Max",
                "description": "...",
                "price": 39900.00,
                "stock_quantity": 50,
                "is_active": True,
                "images": [
                    {"url": "https://example.com/main.jpg", "is_primary": True},
                    {"url": "https://example.com/side.jpg", "is_primary": False},
                ],
                "category_ids": [1, 2],
            }
        }
    )
