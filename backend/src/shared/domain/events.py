import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from src.shared.utils.time_utils import now_utc

class DomainEvent(BaseModel):
    """ 所有領域事件的基底類別 """

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = Field(default_factory=now_utc)

    @property
    def event_name(self) -> str:
        return type(self).__name__
