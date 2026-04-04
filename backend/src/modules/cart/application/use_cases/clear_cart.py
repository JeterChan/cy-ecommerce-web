from modules.cart.domain.repository import ICartRepository


class ClearCartUseCase:
    """清空購物車的業務邏輯"""

    def __init__(self, repository: ICartRepository):
        self.repository = repository

    async def execute(self, owner_id: str) -> None:
        await self.repository.clear_cart(owner_id)
