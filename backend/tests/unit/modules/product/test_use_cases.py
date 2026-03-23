import pytest
from unittest.mock import AsyncMock
from decimal import Decimal
from uuid import uuid4

from modules.product.domain.entities import Product, ProductImage
from modules.product.application.use_cases.create_product import CreateProductUseCase
from modules.product.application.use_cases.adjust_product_stock import AdjustProductStockUseCase
from modules.product.application.dtos.product_create_dto import ProductCreateDTO, ProductImageCreateDTO


# ── CreateProductUseCase ──


class TestCreateProductUseCase:
    @pytest.fixture
    def product_repo(self):
        repo = AsyncMock()
        created = Product(
            id=uuid4(),
            name="測試商品",
            description="描述",
            price=Decimal("199.00"),
            stock_quantity=50,
            images=[ProductImage(url="https://example.com/img.jpg", is_primary=True)],
        )
        repo.create.return_value = created
        return repo

    @pytest.fixture
    def stock_service(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_create_product_success_with_redis_init(self, product_repo, stock_service):
        use_case = CreateProductUseCase(product_repo, stock_service)
        dto = ProductCreateDTO(
            name="測試商品",
            description="描述",
            price=Decimal("199.00"),
            stock_quantity=50,
            images=[ProductImageCreateDTO(url="https://example.com/img.jpg", is_primary=True)],
            category_ids=[1],
        )

        result = await use_case.execute(dto)

        product_repo.create.assert_called_once()
        stock_service.init_stock.assert_called_once_with(result.id, result.stock_quantity)

    @pytest.mark.asyncio
    async def test_create_product_without_stock_service(self, product_repo):
        use_case = CreateProductUseCase(product_repo, stock_service=None)
        dto = ProductCreateDTO(
            name="測試商品",
            description="描述",
            price=Decimal("199.00"),
            stock_quantity=50,
            images=[ProductImageCreateDTO(url="https://example.com/img.jpg", is_primary=True)],
        )

        result = await use_case.execute(dto)

        product_repo.create.assert_called_once()
        assert result is not None


# ── AdjustProductStockUseCase ──


class TestAdjustProductStockUseCase:
    @pytest.fixture
    def existing_product(self):
        return Product(
            id=uuid4(),
            name="測試商品",
            description=None,
            price=Decimal("100"),
            stock_quantity=20,
        )

    @pytest.fixture
    def product_repo(self, existing_product):
        repo = AsyncMock()
        repo.get_by_id.return_value = existing_product
        repo.update.side_effect = lambda p: p
        return repo

    @pytest.fixture
    def stock_service(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_adjust_stock_success_and_redis_sync(
        self, product_repo, stock_service, existing_product
    ):
        use_case = AdjustProductStockUseCase(product_repo, stock_service)
        product_id = existing_product.id

        result = await use_case.execute(product_id, 5)

        assert result.stock_quantity == 25
        product_repo.update.assert_called_once()
        stock_service.sync_stock.assert_called_once_with(product_id, 5)

    @pytest.mark.asyncio
    async def test_adjust_stock_insufficient_raises(
        self, product_repo, stock_service, existing_product
    ):
        use_case = AdjustProductStockUseCase(product_repo, stock_service)

        with pytest.raises(ValueError, match="庫存不足"):
            await use_case.execute(existing_product.id, -30)

        stock_service.sync_stock.assert_not_called()

    @pytest.mark.asyncio
    async def test_adjust_stock_product_not_found(self, stock_service):
        repo = AsyncMock()
        repo.get_by_id.return_value = None
        use_case = AdjustProductStockUseCase(repo, stock_service)

        with pytest.raises(ValueError, match="不存在"):
            await use_case.execute(uuid4(), 5)
