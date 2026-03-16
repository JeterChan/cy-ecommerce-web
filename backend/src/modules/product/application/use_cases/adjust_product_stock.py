from uuid import UUID
from modules.product.domain.entities import Product
from modules.product.domain.repository import IProductRepository


class AdjustProductStockUseCase:
    """調整商品庫存的業務邏輯"""

    def __init__(self, repo: IProductRepository):
        self.repo = repo

    async def execute(self, product_id: UUID, quantity_change: int) -> Product:
        """
        執行調整商品庫存

        Args:
            product_id: 商品 UUID
            quantity_change: 庫存變化量（正數增加，負數減少）

        Returns:
            更新後的商品 Entity

        Raises:
            ValueError: 商品不存在或庫存不足
        """
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise ValueError(f"商品 UUID {product_id} 不存在")

        product.update_stock(quantity_change)

        return await self.repo.update(product)
