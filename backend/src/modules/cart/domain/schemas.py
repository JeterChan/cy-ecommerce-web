from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid

class CartItemBase(BaseModel):
    """購物車項目基礎 Base"""
    product_id: uuid.UUID = Field(..., description="商品 UUID")
    quantity: int = Field(..., gt=0, description="數量(必須大於0)")

class CartItemCreate(CartItemBase):
    """新增購物車項目"""
    pass

class CartItemUpdate(BaseModel):
    """更新購物車項目"""
    quantity: int = Field(..., gt=0, description="更新後的數量")

class CartItemResponse(CartItemBase):
    """購物車項目回應"""
    id: uuid.UUID = Field(..., description="購物車項目 UUID")
    user_id: Optional[uuid.UUID] = Field(None, description="會員 UUID (訪客為 None)")
    guest_token: Optional[str] = Field(None, description="訪客識別碼")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

