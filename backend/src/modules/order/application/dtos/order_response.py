from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from modules.order.application.dtos.order_item_response import OrderItemResponse

class OrderResponse(BaseModel):
    id: UUID
    order_number: str
    user_id: UUID
    status: str
    total_amount: Decimal
    shipping_fee: Decimal
    recipient_name: str
    recipient_phone: str
    shipping_address: str
    payment_method: str
    note: str | None = None
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime
    status_updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
