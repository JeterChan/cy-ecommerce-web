from typing import Optional, TYPE_CHECKING

from modules.product.domain.entities import Product, ProductImage
from modules.product.application.dtos import ProductCreateDTO
from modules.product.domain.repository import IProductRepository

if TYPE_CHECKING:
    from infrastructure.stock_redis_service import StockRedisService


class CreateProductUseCase:
    """建立商品的業務邏輯"""

    def __init__(
        self,
        repo: IProductRepository,
        stock_service: Optional["StockRedisService"] = None,
    ):
        self.repo = repo
        self.stock_service = stock_service

    async def execute(self, data: ProductCreateDTO) -> Product:
        """
        執行建立商品

        Args:
            data: 建立商品的 Input DTO

        Returns:
            建立的商品 Entity

        Raises:
            ValueError: 商品資料驗證失敗
        """
        images = [
            ProductImage(url=img.url, alt_text=img.alt_text, is_primary=img.is_primary)
            for img in data.images
        ]

        category_id = data.category_ids[0] if data.category_ids else None

        product = Product(
            name=data.name,
            description=data.description,
            price=data.price,
            stock_quantity=data.stock_quantity,
            is_active=data.is_active,
            images=images,
            category_id=category_id,
        )

        product.validate()

        created = await self.repo.create(product)

        # 同步 Redis 庫存
        if self.stock_service and created.id:
            await self.stock_service.init_stock(created.id, created.stock_quantity)

        return created
