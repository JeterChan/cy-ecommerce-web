import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from src.shared.utils.time_utils import now_utc


class BaseEntity(BaseModel):
    """所有 Domain Entity 的父類別"""

    # 使用 UUID v4 作為 ID
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # 自動記錄時間
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)

    # Pydantic v2 設定：允許從 ORM 物件讀取資料
    model_config = {"from_attributes": True}

    def __eq__(self, other):
        if isinstance(other, BaseEntity):
            return self.id == other.id
        return False
