from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from typing import Optional, List

class ProductUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    image_url: Optional[str] = Field(None, max_length=255)
    category_ids: Optional[List[int]] = None
    model_config = ConfigDict(json_schema_extra={"example": {"price": 35900.00, "stock_quantity": 30, "is_active": True}})
