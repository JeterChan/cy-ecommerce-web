"""
Cart Query Use Cases

處理讀取購物車資料的業務邏輯（Queries）
包含：取得購物車、查詢單一商品、計算摘要
"""
import uuid
from typing import List, Optional

from modules.cart.domain.repository import ICartRepository
from modules.cart.domain.entities import CartItemResponse


class GetCartUseCase:
    """取得購物車的業務邏輯"""

    def __init__(self, repository: ICartRepository):
        """
        初始化 Use Case

        Args:
            repository: ICartRepository 實作（RedisCartRepository 或 SQLCartRepository）
        """
        self.repository = repository

    async def execute(self, owner_id: str) -> List[CartItemResponse]:
        """
        執行取得購物車所有商品

        Args:
            owner_id: 擁有者識別

        Returns:
            List[CartItemResponse]: 購物車項目列表（可能為空）
        """
        return await self.repository.get_cart(owner_id)


class GetCartItemUseCase:
    """查詢購物車中單一商品的業務邏輯"""

    def __init__(self, repository: ICartRepository):
        self.repository = repository

    async def execute(
        self,
        owner_id: str,
        product_id: uuid.UUID
    ) -> Optional[CartItemResponse]:
        """
        執行查詢購物車中的單一商品

        Args:
            owner_id: 擁有者識別
            product_id: 商品 UUID

        Returns:
            Optional[CartItemResponse]: 購物車項目，若不存在則回傳 None
        """
        return await self.repository.get_item(owner_id, product_id)


class GetCartSummaryUseCase:
    """計算購物車摘要的業務邏輯"""

    def __init__(self, repository: ICartRepository):
        self.repository = repository

    async def execute(self, owner_id: str) -> dict:
        """
        執行計算購物車摘要

        Args:
            owner_id: 擁有者識別

        Returns:
            dict: 包含 total_quantity（總數量）和 total_items（商品種類數）

        注意:
            購物車不儲存價格，總金額需要前端動態查詢 Product 計算
        """
        items = await self.repository.get_cart(owner_id)

        return {
            "total_quantity": sum(item.quantity for item in items),
            "total_items": len(items)
        }

