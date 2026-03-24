import pytest
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal
from uuid import uuid4

from modules.cart.application.use_cases.cart_commands import (
    AddToCartUseCase,
    UpdateCartItemQuantityUseCase,
)
from modules.cart.domain.exceptions import InsufficientStockException
from modules.product.domain.entities import Product


def _make_product(stock=10, **kw):
    defaults = dict(
        id=uuid4(), name="測試商品", description=None,
        price=Decimal("100"), stock_quantity=stock,
    )
    defaults.update(kw)
    return Product(**defaults)


# ── AddToCartUseCase ──


class TestAddToCartUseCase:
    @pytest.fixture
    def cart_repo(self):
        repo = AsyncMock()
        repo.get_item.return_value = None  # no existing item
        repo.add_item.return_value = MagicMock()
        return repo

    @pytest.fixture
    def product_repo(self):
        repo = AsyncMock()
        repo.get_by_id.return_value = _make_product(stock=10)
        return repo

    @pytest.mark.asyncio
    async def test_add_to_cart_success(self, cart_repo, product_repo):
        use_case = AddToCartUseCase(cart_repo, product_repo)
        product_id = product_repo.get_by_id.return_value.id

        await use_case.execute("owner-1", product_id, 3)

        cart_repo.add_item.assert_called_once_with("owner-1", product_id, 3)

    @pytest.mark.asyncio
    async def test_add_to_cart_accumulate_exceeds_stock(self, cart_repo, product_repo):
        # 現有 7 件，再加 5 件 → 12 > 10
        existing = MagicMock()
        existing.quantity = 7
        cart_repo.get_item.return_value = existing

        use_case = AddToCartUseCase(cart_repo, product_repo)
        product_id = product_repo.get_by_id.return_value.id

        with pytest.raises(InsufficientStockException):
            await use_case.execute("owner-1", product_id, 5)

        cart_repo.add_item.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_to_cart_product_not_found(self, cart_repo):
        product_repo = AsyncMock()
        product_repo.get_by_id.return_value = None

        use_case = AddToCartUseCase(cart_repo, product_repo)

        with pytest.raises(ValueError, match="not found"):
            await use_case.execute("owner-1", uuid4(), 1)


# ── UpdateCartItemQuantityUseCase ──


class TestUpdateCartItemQuantityUseCase:
    @pytest.fixture
    def cart_repo(self):
        repo = AsyncMock()
        repo.update_quantity.return_value = MagicMock()
        return repo

    @pytest.fixture
    def product_repo(self):
        repo = AsyncMock()
        repo.get_by_id.return_value = _make_product(stock=10)
        return repo

    @pytest.mark.asyncio
    async def test_update_quantity_exceeds_stock(self, cart_repo, product_repo):
        use_case = UpdateCartItemQuantityUseCase(cart_repo, product_repo)
        product_id = product_repo.get_by_id.return_value.id

        with pytest.raises(InsufficientStockException):
            await use_case.execute("owner-1", product_id, 15)

        cart_repo.update_quantity.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_quantity_success(self, cart_repo, product_repo):
        use_case = UpdateCartItemQuantityUseCase(cart_repo, product_repo)
        product_id = product_repo.get_by_id.return_value.id

        await use_case.execute("owner-1", product_id, 5)

        cart_repo.update_quantity.assert_called_once_with("owner-1", product_id, 5)
