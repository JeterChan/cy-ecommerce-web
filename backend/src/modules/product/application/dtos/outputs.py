"""
Product Output DTOs

用於回傳給 API 的響應資料
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ProductResponseDTO(BaseModel):
    """
    商品完整資訊的 Output DTO

    用於 GET /products/{id} 和 POST /products 的回應
    包含所有商品資訊及系統欄位
    """
    id: UUID = Field(..., description="商品 UUID")
    name: str = Field(..., description="商品名稱")
    description: Optional[str] = Field(None, description="商品描述")
    price: Decimal = Field(..., description="商品價格")
    stock_quantity: int = Field(..., description="庫存數量")
    is_active: bool = Field(..., description="是否上架")
    image_url: Optional[str] = Field(None, description="商品圖片 URL")
    category_ids: List[int] = Field(default_factory=list, description="分類 ID 列表")
    created_at: datetime = Field(..., description="建立時間")
    updated_at: datetime = Field(..., description="更新時間")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
                "name": "iPhone 15 Pro Max",
                "description": "Apple 最新旗艦手機，搭載 A17 Pro 晶片，6.7 吋 Super Retina XDR 顯示器",
                "price": 39900.00,
                "stock_quantity": 50,
                "is_active": True,
                "image_url": "https://example.com/images/iphone-15-pro-max.jpg",
                "category_ids": [1, 2, 5],
                "created_at": "2026-02-15T10:30:00Z",
                "updated_at": "2026-02-15T10:30:00Z"
            }
        }
    )

    @field_validator('category_ids', mode='before')
    @classmethod
    def extract_category_ids(cls, v, info):
        if hasattr(v, '__iter__') and not isinstance(v, (str, bytes)):
            return [cat.id for cat in v if hasattr(cat, 'id')]
        return v or []


class ProductListItemDTO(BaseModel):
    """
    商品列表項目的 Output DTO

    用於 GET /products 的回應
    提供精簡的商品資訊用於列表頁
    """
    id: int = Field(..., description="商品 ID")
    name: str = Field(..., description="商品名稱")
    price: Decimal = Field(..., description="商品價格")
    stock_quantity: int = Field(..., description="庫存數量")
    is_active: bool = Field(..., description="是否上架")
    image_url: Optional[str] = Field(None, description="商品圖片 URL")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "iPhone 15 Pro Max",
                "price": 39900.00,
                "stock_quantity": 50,
                "is_active": True,
                "image_url": "https://example.com/images/iphone-15-pro-max.jpg"
            }
        }
    )

