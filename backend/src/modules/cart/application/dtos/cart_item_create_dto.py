from pydantic import BaseModel, Field
import uuid


class CartItemCreateDTO(BaseModel):
    product_id: uuid.UUID = Field(...)
    quantity: int = Field(..., gt=0)
