from uuid import UUID
from modules.product.domain.repository import IProductRepository


class DeleteProductUseCase:
    """刪除商品的業務邏輯"""

    def __init__(self, repo: IProductRepository):
        self.repo = repo

    async def execute(self, product_id: UUID) -> bool:
        """
        執行刪除商品

        Args:
            product_id: 商品 UUID

        Returns:
            是否刪除成功

        Raises:
            ValueError: 商品不存在
        """
        success = await self.repo.delete(product_id)
        if not success:
            raise ValueError(f"商品 UUID {product_id} 不存在")
        return success
