from pydantic import BaseModel, Field
from typing import List
from modules.order.application.dtos.order_response import OrderResponse


class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int
    skip: int
    limit: int
