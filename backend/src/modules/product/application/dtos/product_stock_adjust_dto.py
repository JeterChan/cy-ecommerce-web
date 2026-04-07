from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ProductStockAdjustDTO(BaseModel):
    quantity_change: int = Field(...)
    reason: Optional[str] = Field(None, max_length=200)
    model_config = ConfigDict(
        json_schema_extra={"example": {"quantity_change": 10, "reason": "補貨入庫"}}
    )
