from uuid import UUID
from typing import Optional, TYPE_CHECKING

from modules.product.domain.entities import Product
from modules.product.domain.repository import IProductRepository

if TYPE_CHECKING:
    from infrastructure.stock_redis_service import StockRedisService


class AdjustProductStockUseCase:
    """調整商品庫存的業務邏輯"""

    def __init__(
        self,
        repo: IProductRepository,
        stock_service: Optional["StockRedisService"] = None,
    ):
        self.repo = repo
        self.stock_service = stock_service

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

        updated = await self.repo.update(product)

        # 同步 Redis 庫存
        if self.stock_service:
            await self.stock_service.sync_stock(product_id, quantity_change)

        return updated
