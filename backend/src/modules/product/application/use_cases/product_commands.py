"""
Product Command Use Cases

處理修改資料的業務邏輯（Commands）
"""
from sqlalchemy.ext.asyncio import AsyncSession
from modules.product.domain.entities import Product
from modules.product.infrastructure.repositories import SqlAlchemyProductRepository
from modules.product.application.dtos import ProductCreateDTO, ProductUpdateDTO


class CreateProductUseCase:
    """建立商品的業務邏輯"""

    def __init__(self, db: AsyncSession):
        self.repo = SqlAlchemyProductRepository(db)

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
        # DTO -> Domain Entity
        product = Product(
            name=data.name,
            description=data.description,
            price=data.price,
            stock_quantity=data.stock_quantity,
            is_active=data.is_active,
            image_url=data.image_url,
            category_ids=data.category_ids or []
        )

        # 業務驗證
        product.validate()

        # 儲存
        return await self.repo.create(product)


class UpdateProductUseCase:
    """更新商品的業務邏輯"""

    def __init__(self, db: AsyncSession):
        self.repo = SqlAlchemyProductRepository(db)

    async def execute(self, product_id: int, data: ProductUpdateDTO) -> Product:
        """
        執行更新商品（部分更新）

        Args:
            product_id: 商品 ID
            data: 更新商品的 Input DTO

        Returns:
            更新後的商品 Entity

        Raises:
            ValueError: 商品不存在或驗證失敗
        """
        # 取得現有商品
        existing = await self.repo.get_by_id(product_id)
        if not existing:
            raise ValueError(f"商品 ID {product_id} 不存在")

        # 只更新提供的欄位
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing, key, value)

        # 業務驗證
        existing.validate()

        # 儲存
        return await self.repo.update(existing)


class DeleteProductUseCase:
    """刪除商品的業務邏輯"""

    def __init__(self, db: AsyncSession):
        self.repo = SqlAlchemyProductRepository(db)

    async def execute(self, product_id: int) -> bool:
        """
        執行刪除商品

        Args:
            product_id: 商品 ID

        Returns:
            是否刪除成功

        Raises:
            ValueError: 商品不存在
        """
        success = await self.repo.delete(product_id)
        if not success:
            raise ValueError(f"商品 ID {product_id} 不存在")
        return success


class ToggleProductActiveUseCase:
    """切換商品上下架狀態的業務邏輯"""

    def __init__(self, db: AsyncSession):
        self.repo = SqlAlchemyProductRepository(db)

    async def execute(self, product_id: int) -> Product:
        """
        執行切換商品上下架狀態

        Args:
            product_id: 商品 ID

        Returns:
            更新後的商品 Entity

        Raises:
            ValueError: 商品不存在
        """
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise ValueError(f"商品 ID {product_id} 不存在")

        # 使用 Domain Entity 的業務方法
        if product.is_active:
            product.deactivate()
        else:
            product.activate()

        return await self.repo.update(product)


class AdjustProductStockUseCase:
    """調整商品庫存的業務邏輯"""

    def __init__(self, db: AsyncSession):
        self.repo = SqlAlchemyProductRepository(db)

    async def execute(self, product_id: int, quantity_change: int) -> Product:
        """
        執行調整商品庫存

        Args:
            product_id: 商品 ID
            quantity_change: 庫存變化量（正數增加，負數減少）

        Returns:
            更新後的商品 Entity

        Raises:
            ValueError: 商品不存在或庫存不足
        """
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise ValueError(f"商品 ID {product_id} 不存在")

        # 使用 Domain Entity 的業務方法
        product.update_stock(quantity_change)

        return await self.repo.update(product)

