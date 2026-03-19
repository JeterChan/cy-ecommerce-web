from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from typing import List, Optional, Tuple
from uuid import UUID
from modules.product.domain.repository import IProductRepository
from modules.product.domain.entities import Product, ProductImage
from modules.product.infrastructure.models import ProductModel, ProductImageModel, CategoryModel

class SqlAlchemyProductRepository(IProductRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

# _fetch_category_models removed

    async def create(self, product: Product) -> Product:
        model = self._to_model(product)
        model.category_id = product.category_id

        self.db.add(model)
        await self.db.flush()
        await self.db.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        stmt = select(ProductModel).where(ProductModel.id == product_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list(self, skip: int = 0, limit: int = 100, category_id: Optional[int] = None, category_ids: Optional[List[int]] = None, is_active: Optional[bool] = None) -> Tuple[List[Product], int]:
        stmt = select(ProductModel)
        count_stmt = select(func.count()).select_from(ProductModel)

        if is_active is not None:
            stmt = stmt.where(ProductModel.is_active == is_active)
            count_stmt = count_stmt.where(ProductModel.is_active == is_active)
        
        if category_ids:
            stmt = stmt.where(ProductModel.category_id.in_(category_ids))
            count_stmt = count_stmt.where(ProductModel.category_id.in_(category_ids))
        elif category_id:
            stmt = stmt.where(ProductModel.category_id == category_id)
            count_stmt = count_stmt.where(ProductModel.category_id == category_id)

        # 執行總數查詢
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        # 分頁與排序
        stmt = stmt.order_by(ProductModel.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models], total

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
            stmt = stmt.where(ProductModel.category_id == category_id)
            count_stmt = count_stmt.where(ProductModel.category_id == category_id)

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
        model.category_id = product.category_id

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

        await self.db.flush()
        await self.db.refresh(model)
        return self._to_entity(model)

    async def atomic_adjust_stock(self, product_id: UUID, quantity_change: int) -> Product:
        """實作 T016a: 原子扣減庫存 (使用 with_for_update)"""
        # 注意：必須加上 populate_existing() 確保屬性會重新從資料庫載入
        stmt = select(ProductModel).where(ProductModel.id == product_id).with_for_update(of=ProductModel).execution_options(populate_existing=True)
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

    async def count_total_active(self) -> int:
        """計算啟用中的商品總數"""
        stmt = select(func.count()).select_from(ProductModel).where(ProductModel.is_active == True)
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def count_low_stock(self) -> int:
        """計算低庫存商品數（is_active=True 且 0 < stock_quantity < 5）"""
        stmt = (
            select(func.count())
            .select_from(ProductModel)
            .where(ProductModel.is_active == True)
            .where(ProductModel.stock_quantity > 0)
            .where(ProductModel.stock_quantity < 5)
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def delete(self, product_id: UUID) -> bool:
        stmt = select(ProductModel).where(ProductModel.id == product_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return False

        await self.db.delete(model)
        await self.db.flush()
        return True

    async def get_by_ids_with_lock(self, product_ids: List[UUID]) -> List[Product]:
        """實作：批量鎖定商品 (悲觀鎖)"""
        if not product_ids:
            return []
        
        # 按照 ID 排序以防止死鎖 (Deadlock Prevention)
        # 注意：必須加上 populate_existing() 確保屬性會重新從資料庫載入
        stmt = select(ProductModel).where(ProductModel.id.in_(product_ids))\
            .order_by(ProductModel.id.asc())\
            .with_for_update(of=ProductModel)\
            .execution_options(populate_existing=True)
        
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

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
        category_id = model.category_id
        category_name = model.category.name if model.category else None

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
            category_id=category_id,
            category_name=category_name,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

