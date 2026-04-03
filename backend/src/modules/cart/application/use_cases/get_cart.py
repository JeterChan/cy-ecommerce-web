from typing import List

from modules.cart.domain.repository import ICartRepository
from modules.cart.domain.entities import CartItemResponse


class GetCartUseCase:
    """取得購物車的業務邏輯"""

    def __init__(self, repository: ICartRepository):
        self.repository = repository

    async def execute(self, owner_id: str) -> List[CartItemResponse]:
        return await self.repository.get_cart(owner_id)
