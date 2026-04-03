from typing import List

from modules.cart.domain.repository import ICartRepository
from modules.cart.domain.entities import CartItemResponse, CartItemCreate


class BatchAddToCartUseCase:
    """批量新增商品到購物車的業務邏輯"""

    def __init__(self, repository: ICartRepository):
        self.repository = repository

    async def execute(
        self,
        owner_id: str,
        items: List[CartItemCreate]
    ) -> List[CartItemResponse]:
        """
        執行批量新增商品到購物車

        使用場景: 購物車合併
        """
        return await self.repository.batch_add_items(owner_id, items)
