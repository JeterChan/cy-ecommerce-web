"""
Cart Module - Product Info Adapter

橋接 Product 模組的 SqlAlchemyProductRepository，
實作 Cart 模組的 IProductInfoPort 介面。
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from modules.cart.domain.ports import IProductInfoPort, ProductSnapshot
from modules.product.infrastructure.repository import SqlAlchemyProductRepository


class ProductInfoAdapter(IProductInfoPort):
    """
    商品資訊適配器

    將 Product 模組的 Repository 適配為 Cart 模組的 Port 介面，
    並將 Product Entity 轉換為 Cart 模組的 ProductSnapshot 值物件。
    """

    def __init__(self, db: AsyncSession):
        self._product_repo = SqlAlchemyProductRepository(db)

    async def get_product_info(self, product_id: UUID) -> Optional[ProductSnapshot]:
        product = await self._product_repo.get_by_id(product_id)
        if not product:
            return None
        return self._to_snapshot(product)

    async def get_products_info(self, product_ids: List[UUID]) -> List[ProductSnapshot]:
        snapshots = []
        for pid in product_ids:
            product = await self._product_repo.get_by_id(pid)
            if product:
                snapshots.append(self._to_snapshot(product))
        return snapshots

    @staticmethod
    def _to_snapshot(product) -> ProductSnapshot:
        image_url = None
        if product.images:
            primary = next((img for img in product.images if img.is_primary), None)
            image_url = (
                (primary or product.images[0]).url
                if (primary or product.images)
                else None
            )

        return ProductSnapshot(
            id=product.id,
            name=product.name,
            price=product.price,
            stock_quantity=product.stock_quantity,
            is_active=product.is_active,
            image_url=image_url,
        )
