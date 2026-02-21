"""
Product Input DTOs

用於接收來自 API 的請求資料
"""
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from typing import Optional, List


class ProductBase(BaseModel):
    """Product 基礎欄位"""
    name: str = Field(..., min_length=1, max_length=100, description="商品名稱")
    description: Optional[str] = Field(None, max_length=500, description="商品描述")
    price: Decimal = Field(..., gt=0, decimal_places=2, description="商品價格")
    stock_quantity: int = Field(..., ge=0, description="庫存數量")
    is_active: bool = Field(default=True, description="是否上架")
    image_url: Optional[str] = Field(None, max_length=255, description="商品圖片 URL")
    category_ids: Optional[List[int]] = Field(default_factory=list, description="分類 ID 列表")


class ProductCreateDTO(ProductBase):
    """
    建立商品的 Input DTO

    用於 POST /products
    所有必填欄位都要提供
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "iPhone 15 Pro Max",
                "description": "Apple 最新旗艦手機，搭載 A17 Pro 晶片，6.7 吋 Super Retina XDR 顯示器",
                "price": 39900.00,
                "stock_quantity": 50,
                "is_active": True,
                "image_url": "https://example.com/images/iphone-15-pro-max.jpg",
                "category_ids": [1, 2, 5]
            }
        }
    )


class ProductUpdateDTO(BaseModel):
    """
    更新商品的 Input DTO

    用於 PUT/PATCH /products/{id}
    所有欄位都是選填（部分更新）
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="商品名稱")
    description: Optional[str] = Field(None, max_length=500, description="商品描述")
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2, description="商品價格")
    stock_quantity: Optional[int] = Field(None, ge=0, description="庫存數量")
    is_active: Optional[bool] = Field(None, description="是否上架")
    image_url: Optional[str] = Field(None, max_length=255, description="商品圖片 URL")
    category_ids: Optional[List[int]] = Field(None, description="分類 ID 列表")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "price": 35900.00,
                "stock_quantity": 30,
                "is_active": True
            }
        }
    )


class ProductStockAdjustDTO(BaseModel):
    """
    調整庫存的 Input DTO

    用於 POST /products/{id}/adjust-stock
    """
    quantity_change: int = Field(..., description="庫存變化量（正數增加，負數減少）")
    reason: Optional[str] = Field(None, max_length=200, description="調整原因")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quantity_change": 10,
                "reason": "補貨入庫"
            }
        }
    )

