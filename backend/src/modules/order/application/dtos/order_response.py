from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import List
from modules.order.application.dtos.order_item_response import OrderItemResponse

class OrderResponse(BaseModel):
    id: int
    user_id: str
    status: str
    total_amount: Decimal
    shipping_fee: Decimal
    note: str | None = None
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
