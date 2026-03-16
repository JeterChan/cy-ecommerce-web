"""
Order Module - Output DTOs

此檔案定義 API 回應的 Pydantic 模型。
"""

from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID


class OrderItemResponse(BaseModel):
    """訂單項目回應 DTO"""

    id: int = Field(..., description="訂單項目 ID")
    order_id: int = Field(..., description="所屬訂單 ID")
    product_id: UUID = Field(..., description="商品 UUID")
    product_name: str = Field(..., description="商品名稱（購買時的快照）")
    quantity: int = Field(..., description="購買數量", ge=1)
    unit_price: Decimal = Field(..., description="單價（購買時的快照）")
    subtotal: Decimal = Field(..., description="小計（單價 × 數量）")
    created_at: datetime = Field(..., description="建立時間")
    updated_at: datetime = Field(..., description="更新時間")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "order_id": 101,
                "product_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
                "product_name": "商品名稱範例",
                "quantity": 2,
                "unit_price": 299.99,
                "subtotal": 599.98,
                "created_at": "2026-02-21T10:30:00",
                "updated_at": "2026-02-21T10:30:00"
            }
        }
    }


class OrderResponse(BaseModel):
    """訂單回應 DTO"""

    id: int = Field(..., description="訂單 ID")
    user_id: str = Field(..., description="使用者 ID")
    status: str = Field(..., description="訂單狀態")
    total_amount: Decimal = Field(..., description="訂單總金額")
    shipping_fee: Decimal = Field(..., description="運費")
    note: str | None = Field(None, description="訂單備註")
    items: List[OrderItemResponse] = Field(..., description="訂單項目列表")
    created_at: datetime = Field(..., description="建立時間")
    updated_at: datetime = Field(..., description="更新時間")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 101,
                "user_id": "user-uuid-123",
                "status": "PENDING",
                "total_amount": 659.98,
                "shipping_fee": 60.00,
                "note": "請儘快出貨",
                "items": [
                    {
                        "id": 1,
                        "order_id": 101,
                        "product_id": 42,
                        "product_name": "商品名稱範例",
                        "quantity": 2,
                        "unit_price": 299.99,
                        "subtotal": 599.98,
                        "created_at": "2026-02-21T10:30:00",
                        "updated_at": "2026-02-21T10:30:00"
                    }
                ],
                "created_at": "2026-02-21T10:30:00",
                "updated_at": "2026-02-21T10:30:00"
            }
        }
    }


class OrderListResponse(BaseModel):
    """訂單列表回應 DTO"""

    orders: List[OrderResponse] = Field(..., description="訂單列表")
    total: int = Field(..., description="總筆數")
    skip: int = Field(..., description="略過筆數")
    limit: int = Field(..., description="限制筆數")

    model_config = {
        "json_schema_extra": {
            "example": {
                "orders": [],
                "total": 10,
                "skip": 0,
                "limit": 20
            }
        }
    }


