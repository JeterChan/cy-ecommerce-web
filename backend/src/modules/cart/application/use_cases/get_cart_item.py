import uuid
from typing import Optional

from modules.cart.domain.repository import ICartRepository
from modules.cart.domain.entities import CartItemResponse


class GetCartItemUseCase:
    """查詢購物車中單一商品的業務邏輯"""

    def __init__(self, repository: ICartRepository):
        self.repository = repository

    async def execute(
        self,
        owner_id: str,
        product_id: uuid.UUID
    ) -> Optional[CartItemResponse]:
        return await self.repository.get_item(owner_id, product_id)
