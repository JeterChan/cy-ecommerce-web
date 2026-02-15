from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from modules.product.domain.repository import ProductRepository
from modules.product.domain.entities import Product
from modules.product.infrastructure.models import ProductModel

class SqlAlchemyProductRepository(ProductRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, product: Product) -> Product:
        # 轉換 Domain entity -> SQLAlchemy Model
        model = self._to_model(product)

        self.db.add(model)
        await self.db.flush()  # ✅ 使用 flush 而非 commit
        await self.db.refresh(model)

        # 轉換 SQLAlchemy Model -> Domain Entity
        return self._to_entity(model)

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        stmt = select(ProductModel).where(ProductModel.id == product_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list(self, skip: int = 0, limit: int = 100) -> List[Product]:
        stmt = select(ProductModel).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def update(self, product: Product) -> Product:
        stmt = select(ProductModel).where(ProductModel.id == product.id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            raise ValueError(f"Product with id {product.id} not found")

        model.name = product.name
        model.description = product.description
        model.price = product.price
        model.stock_quantity = product.stock_quantity
        model.is_active = product.is_active
        model.image_url = product.image_url

        await self.db.flush()
        await self.db.refresh(model)
        return self._to_entity(model)

    async def delete(self, product_id: int) -> bool:
        stmt = select(ProductModel).where(ProductModel.id == product_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return False

        await self.db.delete(model)
        await self.db.flush()

        return True

    # noinspection PyMethodMayBeStatic
    def _to_model(self, product: Product) -> ProductModel:
        """Domain Entity -> SQLAlchemy Model"""
        model = ProductModel(
            name=product.name,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
            is_active=product.is_active,
            image_url=product.image_url
        )

        if product.id:
            model.id = product.id

        return model

    # noinspection PyMethodMayBeStatic
    def _to_entity(self, model: ProductModel) -> Product:
        """ 轉換 SQLAlchemy Model 為 Domain Entity"""
        # ✅ 安全地處理 categories 關聯，避免 lazy loading 錯誤
        try:
            category_ids = [c.id for c in model.categories] if model.categories else []
        except Exception:
            # 如果 categories 尚未載入或 session 已關閉，使用空列表
            category_ids = []

        return Product(
            id=model.id,
            name=model.name,
            description=model.description,
            price=model.price,
            stock_quantity=model.stock_quantity,
            is_active=model.is_active,
            image_url=model.image_url,
            category_ids=category_ids,
            created_at=model.created_at,
            updated_at=model.updated_at
        )