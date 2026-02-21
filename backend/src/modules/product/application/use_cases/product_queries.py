"""
Product Query Use Cases

處理查詢資料的業務邏輯（Queries）
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from modules.product.domain.entities import Product
from modules.product.infrastructure.repositories import SqlAlchemyProductRepository


class GetProductUseCase:
    """取得單一商品的業務邏輯"""

    def __init__(self, db: AsyncSession):
        self.repo = SqlAlchemyProductRepository(db)

    async def execute(self, product_id: int) -> Product:
        """
        執行取得單一商品

        Args:
            product_id: 商品 ID

        Returns:
            商品 Entity

        Raises:
            ValueError: 商品不存在
        """
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise ValueError(f"商品 ID {product_id} 不存在")
        return product


class ListProductsUseCase:
    """列出商品清單的業務邏輯"""

    def __init__(self, db: AsyncSession):
        self.repo = SqlAlchemyProductRepository(db)

    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[Product]:
        """
        執行列出商品清單

        Args:
            skip: 略過的筆數
            limit: 取得的筆數上限
            is_active: 是否只顯示上架商品 (None=全部, True=上架, False=下架)

        Returns:
            商品 Entity 列表
        """
        products = await self.repo.list(skip=skip, limit=limit)

        # 依照 is_active 篩選
        if is_active is not None:
            products = [p for p in products if p.is_active == is_active]

        return products

