"""
Order Module - Product Adapter

橋接 Product 模組，實作 Order 模組的 IProductPort 介面。
封裝悲觀鎖查詢、庫存扣減、庫存回補等操作。
"""

from typing import List
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.order.domain.ports import IProductPort, CheckoutProduct
from modules.product.infrastructure.models import ProductModel
from modules.product.infrastructure.repository import SqlAlchemyProductRepository


class OrderProductAdapter(IProductPort):
    """
    訂單模組的商品適配器

    將 Product 模組的 Repository 與 ORM Model 操作封裝為
    Order 模組的 IProductPort 介面。
    """

    def __init__(self, db: AsyncSession):
        self._db = db
        self._product_repo = SqlAlchemyProductRepository(db)

    async def get_products_for_checkout(self, product_ids: List[UUID]) -> List[CheckoutProduct]:
        """取得結帳用商品（含悲觀鎖 FOR UPDATE），按 ID 排序防止死鎖"""
        # populate_existing=True 確保 FOR UPDATE 鎖住的資料列會從資料庫重新載入，
        # 避免 SQLAlchemy identity map 回傳過時的快取物件，導致 stock_quantity 不準確
        stmt = (
            select(ProductModel)
            .where(ProductModel.id.in_(product_ids))
            .with_for_update(of=ProductModel)
            .order_by(ProductModel.id)
            .execution_options(populate_existing=True)
        )
        res = await self._db.execute(stmt)
        models = res.scalars().all()

        return [
            CheckoutProduct(
                id=m.id,
                name=m.name,
                price=Decimal(str(m.price)),
                stock_quantity=m.stock_quantity,
                is_active=m.is_active,
            )
            for m in models
        ]

    async def deduct_stock(self, product_id: UUID, quantity: int) -> None:
        """在現有事務內扣減庫存（直接操作 ORM Model）"""
        stmt = (
            select(ProductModel)
            .where(ProductModel.id == product_id)
            .execution_options(populate_existing=True)
        )
        res = await self._db.execute(stmt)
        model = res.scalar_one()

        model.stock_quantity -= quantity
        self._db.add(model)

    async def restore_stock(self, product_id: UUID, quantity: int) -> None:
        """回補庫存，使用原子操作（FOR UPDATE）"""
        await self._product_repo.atomic_adjust_stock(product_id, quantity)
