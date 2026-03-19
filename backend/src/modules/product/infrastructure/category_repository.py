from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from modules.product.domain.entities import Category
from modules.product.infrastructure.models import CategoryModel


class SqlAlchemyCategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self) -> List[Category]:
        stmt = select(CategoryModel).order_by(CategoryModel.name)
        result = await self.db.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        stmt = select(CategoryModel).where(CategoryModel.id == category_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, category: Category) -> Category:
        model = CategoryModel(name=category.name, slug=category.slug)
        self.db.add(model)
        await self.db.flush()
        await self.db.refresh(model)
        return self._to_entity(model)

    async def update(self, category_id: int, name: Optional[str], slug: Optional[str]) -> Optional[Category]:
        stmt = select(CategoryModel).where(CategoryModel.id == category_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        if name is not None:
            model.name = name
        if slug is not None:
            model.slug = slug
        await self.db.flush()
        await self.db.refresh(model)
        return self._to_entity(model)

    async def delete(self, category_id: int) -> bool:
        stmt = select(CategoryModel).where(CategoryModel.id == category_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.db.delete(model)
        await self.db.flush()
        return True

    def _to_entity(self, model: CategoryModel) -> Category:
        return Category(id=model.id, name=model.name, slug=model.slug)
