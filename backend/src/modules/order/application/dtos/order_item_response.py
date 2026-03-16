from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Optional

class OrderItemResponse(BaseModel):
    id: UUID
    order_id: UUID
    product_id: UUID
    product_name: str
    quantity: int = Field(..., ge=1)
    unit_price: Decimal
    subtotal: Decimal
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
