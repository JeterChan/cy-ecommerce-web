from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
import uuid


class CartItemResponseDTO(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    user_id: Optional[uuid.UUID] = None
    guest_token: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
