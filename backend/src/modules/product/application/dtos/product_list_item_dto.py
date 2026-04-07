from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional


class ProductListItemDTO(BaseModel):
    id: int
    name: str
    price: Decimal
    stock_quantity: int
    is_active: bool
    image_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
