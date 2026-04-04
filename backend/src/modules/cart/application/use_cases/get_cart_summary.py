from modules.cart.domain.repository import ICartRepository


class GetCartSummaryUseCase:
    """計算購物車摘要的業務邏輯"""

    def __init__(self, repository: ICartRepository):
        self.repository = repository

    async def execute(self, owner_id: str) -> dict:
        """
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
