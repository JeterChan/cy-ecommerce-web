from uuid import UUID
from modules.product.domain.entities import Product, ProductImage
from modules.product.application.dtos import ProductUpdateDTO
from modules.product.domain.repository import IProductRepository


class UpdateProductUseCase:
    """更新商品的業務邏輯"""

    def __init__(self, repo: IProductRepository):
        self.repo = repo

    async def execute(self, product_id: UUID, data: ProductUpdateDTO) -> Product:
        """
        執行更新商品（部分更新）

        Args:
            product_id: 商品 UUID
            data: 更新商品的 Input DTO

        Returns:
            更新後的商品 Entity

        Raises:
            ValueError: 商品不存在或驗證失敗
        """
        existing = await self.repo.get_by_id(product_id)
        if not existing:
            raise ValueError(f"商品 UUID {product_id} 不存在")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == 'images':
                existing.images = [
                    ProductImage(
                        url=img['url'],
                        alt_text=img.get('alt_text'),
                        is_primary=img.get('is_primary', False)
                    ) for img in value
                ]
            else:
                setattr(existing, key, value)

        existing.validate()

        return await self.repo.update(existing)
