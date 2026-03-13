from uuid import UUID
from modules.product.domain.entities import Product
from modules.product.domain.repository import IProductRepository


class ToggleProductActiveUseCase:
    """切換商品上下架狀態的業務邏輯"""

    def __init__(self, repo: IProductRepository):
        self.repo = repo

    async def execute(self, product_id: UUID) -> Product:
        """
        執行切換商品上下架狀態

        Args:
            product_id: 商品 UUID

        Returns:
            更新後的商品 Entity

        Raises:
            ValueError: 商品不存在
        """
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise ValueError(f"商品 UUID {product_id} 不存在")

        if product.is_active:
            product.deactivate()
        else:
            product.activate()

        return await self.repo.update(product)
