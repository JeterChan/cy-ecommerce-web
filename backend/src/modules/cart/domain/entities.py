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


class CartItemResponse(BaseModel):
    """購物車項目回應"""
    id: uuid.UUID = Field(..., description="購物車項目 UUID")
    cart_id: uuid.UUID = Field(..., description="購物車 UUID")
    product_id: uuid.UUID = Field(..., description="商品 UUID")
    quantity: int = Field(..., description="數量")
    product_name: Optional[str] = Field(None, description="商品名稱")
    unit_price: float = Field(default=0.0, description="單位價格")
    subtotal: float = Field(default=0.0, description="小計（單價 × 數量）")
    image_url: Optional[str] = Field(None, description="商品圖片 URL")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    """購物車回應"""
    id: uuid.UUID = Field(..., description="購物車 UUID")
    user_id: Optional[uuid.UUID] = Field(None, description="會員 UUID (訪客為 None)")
    guest_token: Optional[str] = Field(None, description="訪客識別碼")
    items: list[CartItemResponse] = Field(default_factory=list, description="購物車項目列表")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CartMergeRequest(BaseModel):
    """購物車合併請求"""
    guest_items: list[dict] = Field(..., description="訪客購物車商品列表")

    model_config = ConfigDict(from_attributes=True)

