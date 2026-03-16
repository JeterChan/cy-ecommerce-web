"""
Order Module - Redis Cart Repository (Adapter)

此檔案提供與 Cart Module Redis Repository 的整合介面。
這是一個適配器模式，將 Cart Module 的 Repository 介面適配給 Order Module 使用。
"""

from typing import List
from modules.order.domain.repository import ICartAdapter
from modules.cart.infrastructure.repositories.redis_repository import RedisCartRepository as CartRedisRepo
from modules.cart.domain.entities import CartItemResponse


class OrderCartAdapter(ICartAdapter):
    """
    訂單模組的購物車適配器

    此類別封裝了與 Cart Module 的互動，提供訂單模組需要的購物車操作。
    """

    def __init__(self, cart_repository: CartRedisRepo):
        """
        初始化購物車適配器

        Args:
            cart_repository: Cart Module 的 RedisCartRepository 實例
        """
        self.cart_repo = cart_repository

    async def get_cart_items(self, owner_id: str) -> List[CartItemResponse]:
        """
        取得使用者的購物車項目

        Args:
            owner_id: 使用者識別（user_id 或 guest_token）

        Returns:
            List[CartItemResponse]: 購物車項目列表
        """
        return await self.cart_repo.get_cart(owner_id)

    async def clear_cart(self, owner_id: str) -> None:
        """
        清空使用者的購物車

        Args:
            owner_id: 使用者識別（user_id 或 guest_token）
        """
        await self.cart_repo.clear_cart(owner_id)

    async def is_cart_empty(self, owner_id: str) -> bool:
        """
        檢查購物車是否為空

        Args:
            owner_id: 使用者識別（user_id 或 guest_token）

        Returns:
            bool: 購物車為空則返回 True
        """
        items = await self.cart_repo.get_cart(owner_id)
        return len(items) == 0


