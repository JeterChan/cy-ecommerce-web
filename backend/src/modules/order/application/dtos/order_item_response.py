from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from uuid import UUID

class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: UUID
    product_name: str
    quantity: int = Field(..., ge=1)
    unit_price: Decimal
    subtotal: Decimal
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
