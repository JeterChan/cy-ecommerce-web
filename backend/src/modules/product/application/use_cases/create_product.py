from modules.product.domain.entities import Product, ProductImage
from modules.product.application.dtos import ProductCreateDTO
from modules.product.domain.repository import IProductRepository


class CreateProductUseCase:
    """建立商品的業務邏輯"""

    def __init__(self, repo: IProductRepository):
        self.repo = repo

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
            ProductImage(
                url=img.url,
                alt_text=img.alt_text,
                is_primary=img.is_primary
            ) for img in data.images
        ]

        product = Product(
            name=data.name,
            description=data.description,
            price=data.price,
            stock_quantity=data.stock_quantity,
            is_active=data.is_active,
            images=images,
            category_ids=data.category_ids or []
        )

        product.validate()

        return await self.repo.create(product)
