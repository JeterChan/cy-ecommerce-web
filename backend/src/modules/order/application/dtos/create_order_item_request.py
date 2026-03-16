from pydantic import BaseModel, Field
from uuid import UUID

class CreateOrderItemRequest(BaseModel):
    product_id: UUID = Field(...)
    quantity: int = Field(..., gt=0)
    model_config = {"json_schema_extra": {"example": {"product_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d", "quantity": 2}}}
