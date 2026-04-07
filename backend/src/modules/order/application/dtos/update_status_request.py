from pydantic import BaseModel
from modules.order.domain.value_objects import OrderStatus


class UpdateStatusRequest(BaseModel):
    status: str
