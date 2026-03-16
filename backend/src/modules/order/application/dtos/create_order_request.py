from pydantic import BaseModel, Field
from decimal import Decimal
from typing import List
from modules.order.application.dtos.create_order_item_request import CreateOrderItemRequest

class CreateOrderRequest(BaseModel):
    items: List[CreateOrderItemRequest] = Field(..., min_length=1)
    shipping_fee: Decimal = Field(default=Decimal("60.00"), ge=0)
    note: str | None = Field(default=None, max_length=500)
