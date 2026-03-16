from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from typing import List, Optional, Tuple
from uuid import UUID
from modules.product.domain.repository import IProductRepository
from modules.product.domain.entities import Product, ProductImage
from modules.product.infrastructure.models import ProductModel, ProductImageModel, CategoryModel, association_table

class SqlAlchemyProductRepository(IProductRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _fetch_category_models(self, category_ids: List[int]) -> List[CategoryModel]:
        """根據 ID 列表取得 CategoryModel 實例"""
        if not category_ids:
            return []
        stmt = select(CategoryModel).where(CategoryModel.id.in_(category_ids))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, product: Product) -> Product:
        model = self._to_model(product)

        if product.category_ids:
            model.categories = await self._fetch_category_models(product.category_ids)

        self.db.add(model)
        await self.db.flush()
        await self.db.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        stmt = select(ProductModel).where(ProductModel.id == product_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list(self, skip: int = 0, limit: int = 100, category_id: Optional[int] = None, is_active: Optional[bool] = None) -> List[Product]:
        stmt = select(ProductModel)
        if is_active is not None:
            stmt = stmt.where(ProductModel.is_active == is_active)
        
        if category_id:
            cat_subquery = select(association_table.c.product_id).where(
                association_table.c.category_id == category_id
            )
            stmt = stmt.where(ProductModel.id.in_(cat_subquery))

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def list_admin(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        sort: str = "created_desc",
    ) -> Tuple[List[Product], int]:
        """管理員專用：支援搜尋、分類篩選、排序、分頁，同時回傳總數"""
        stmt = select(ProductModel)
        count_stmt = select(func.count()).select_from(ProductModel)

        if search:
            stmt = stmt.where(ProductModel.name.ilike(f"%{search}%"))
            count_stmt = count_stmt.where(ProductModel.name.ilike(f"%{search}%"))

        if category_id:
            cat_subquery = select(association_table.c.product_id).where(
                association_table.c.category_id == category_id
            )
            stmt = stmt.where(ProductModel.id.in_(cat_subquery))
            count_stmt = count_stmt.where(ProductModel.id.in_(cat_subquery))

        if sort == "created_asc":
            stmt = stmt.order_by(ProductModel.created_at.asc())
        else:
            stmt = stmt.order_by(ProductModel.created_at.desc())

        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(m) for m in models], total

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

        if product.images:
            model.images = [
                ProductImageModel(
                    url=img.url,
                    alt_text=img.alt_text,
                    is_primary=img.is_primary
                ) for img in product.images
            ]
        else:
            model.images = []

        model.categories = await self._fetch_category_models(product.category_ids)

        await self.db.flush()
        await self.db.refresh(model)
        return self._to_entity(model)

    async def atomic_adjust_stock(self, product_id: UUID, quantity_change: int) -> Product:
        """實作 T016a: 原子扣減庫存 (使用 with_for_update)"""
        stmt = select(ProductModel).where(ProductModel.id == product_id).with_for_update()
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            raise ValueError(f"商品不存在 (id: {product_id})")

        new_quantity = model.stock_quantity + quantity_change
        if new_quantity < 0:
            raise ValueError(f"庫存不足 (現有: {model.stock_quantity}, 預計扣除: {abs(quantity_change)})")

        model.stock_quantity = new_quantity
        await self.db.flush()
        await self.db.refresh(model)
        return self._to_entity(model)

    async def delete(self, product_id: UUID) -> bool:
        stmt = select(ProductModel).where(ProductModel.id == product_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return False

        await self.db.delete(model)
        await self.db.flush()
        return True

    def _to_model(self, product: Product) -> ProductModel:
        """Domain Entity -> SQLAlchemy Model（不含分類，分類需非同步處理）"""
        images = [
            ProductImageModel(
                url=img.url,
                alt_text=img.alt_text,
                is_primary=img.is_primary
            ) for img in product.images
        ]

        model = ProductModel(
            name=product.name,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
            is_active=product.is_active,
            images=images
        )

        if product.id:
            model.id = product.id

        return model

    def _to_entity(self, model: ProductModel) -> Product:
        """轉換 SQLAlchemy Model 為 Domain Entity"""
        category_ids = []
        category_names = []
        try:
            if model.categories:
                category_ids = [c.id for c in model.categories]
                category_names = [c.name for c in model.categories]
        except Exception:
            pass

        try:
            images = [
                ProductImage(
                    id=img.id,
                    url=img.url,
                    alt_text=img.alt_text,
                    is_primary=img.is_primary
                ) for img in model.images
            ] if model.images else []
        except Exception:
            images = []

        return Product(
            id=model.id,
            name=model.name,
            description=model.description,
            price=model.price,
            stock_quantity=model.stock_quantity,
            is_active=model.is_active,
            images=images,
            category_ids=category_ids,
            category_names=category_names,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

