from pydantic import BaseModel, Field
from modules.order.domain.value_objects import PaymentMethod


class CheckoutRequest(BaseModel):
    recipient_name: str = Field(..., min_length=1, max_length=255)
    recipient_phone: str = Field(..., min_length=8, max_length=20)
    shipping_address: str = Field(..., min_length=8, max_length=1000)
    payment_method: PaymentMethod = Field(default=PaymentMethod.COD)
    note: str | None = Field(None, max_length=500)
