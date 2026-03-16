"""
Cart Output DTOs

用於回傳給 API 的響應資料
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid


class CartItemResponseDTO(BaseModel):
    """
    購物車項目的 Output DTO

    用於回傳購物車項目資訊
    """
    id: uuid.UUID = Field(..., description="購物車項目 UUID")
    product_id: uuid.UUID = Field(..., description="商品 UUID")
    quantity: int = Field(..., description="數量")
    user_id: Optional[uuid.UUID] = Field(None, description="會員 UUID（訪客為 None）")
    guest_token: Optional[str] = Field(None, description="訪客識別碼")
    created_at: datetime = Field(..., description="建立時間")
    updated_at: datetime = Field(..., description="更新時間")

    model_config = ConfigDict(from_attributes=True)

