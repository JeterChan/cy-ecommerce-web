from pydantic import BaseModel, Field

class CartItemUpdateDTO(BaseModel):
    quantity: int = Field(..., gt=0)
