import uuid

from modules.cart.domain.repository import ICartRepository


class RemoveFromCartUseCase:
    """從購物車移除商品的業務邏輯"""

    def __init__(self, repository: ICartRepository):
        self.repository = repository

    async def execute(self, owner_id: str, product_id: uuid.UUID) -> None:
        await self.repository.remove_item(owner_id, product_id)
