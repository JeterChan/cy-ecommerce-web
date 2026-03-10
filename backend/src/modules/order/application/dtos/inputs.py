"""
Order Module - Input DTOs

此檔案定義 API 請求的 Pydantic 模型。
"""

from pydantic import BaseModel, Field
from decimal import Decimal
from typing import List
from uuid import UUID


class CreateOrderItemRequest(BaseModel):
    """建立訂單項目請求 DTO"""

    product_id: UUID = Field(
        ...,
        description="商品 UUID"
    )
    quantity: int = Field(
        ...,
        description="購買數量",
        gt=0
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "product_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
                "quantity": 2
            }
        }
    }


class CreateOrderRequest(BaseModel):
    """建立訂單請求 DTO"""

    items: List[CreateOrderItemRequest] = Field(
        ...,
        description="訂單商品列表",
        min_length=1
    )
    shipping_fee: Decimal = Field(
        default=Decimal("60.00"),
        description="運費",
        ge=0
    )
    note: str | None = Field(
        default=None,
        description="訂單備註",
        max_length=500
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {
                        "product_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
                        "quantity": 2
                    },
                    {
                        "product_id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
                        "quantity": 1
                    }
                ],
                "shipping_fee": 100.00,
                "note": "請儘快出貨"
            }
        }
    }


class UpdateOrderStatusRequest(BaseModel):
    """更新訂單狀態請求 DTO"""

    status: str = Field(
        ...,
        description="訂單狀態",
        pattern="^(PENDING|PAID|SHIPPED|COMPLETED|CANCELLED|REFUNDED)$"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "PAID"
            }
        }
    }


