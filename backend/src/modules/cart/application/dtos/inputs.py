"""
Cart Input DTOs

用於接收來自 API 的請求資料
"""
from pydantic import BaseModel, Field
import uuid


class CartItemCreateDTO(BaseModel):
    """
    新增購物車項目的 Input DTO

    用於 POST /cart/items
    """
    product_id: uuid.UUID = Field(..., description="商品 UUID")
    quantity: int = Field(..., gt=0, description="數量（必須大於 0）")


class CartItemUpdateDTO(BaseModel):
    """
    更新購物車項目的 Input DTO

    用於 PUT /cart/items/{id}
    """
    quantity: int = Field(..., gt=0, description="更新後的數量（必須大於 0）")

