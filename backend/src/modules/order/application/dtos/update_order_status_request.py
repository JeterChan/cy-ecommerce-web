from pydantic import BaseModel, Field

class UpdateOrderStatusRequest(BaseModel):
    status: str = Field(..., pattern="^(PENDING|PAID|SHIPPED|COMPLETED|CANCELLED|REFUNDED)$")
