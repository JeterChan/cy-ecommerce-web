import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from modules.cart.application.use_cases.merge_cart import MergeCartUseCase


class TestMergeCartUseCase:
    @pytest.fixture
    def cart_repo(self):
        repo = AsyncMock()
        repo.get_cart.return_value = []
        repo.get_item.return_value = None
        repo.add_item.return_value = MagicMock()
        repo.update_quantity.return_value = MagicMock()
        return repo

    @pytest.mark.asyncio
    async def test_merge_empty_guest_cart_returns_user_cart(self, cart_repo):
        use_case = MergeCartUseCase(cart_repo)
        result = await use_case.execute("user-1", [])

        cart_repo.get_cart.assert_called_once_with("user-1")
        cart_repo.add_item.assert_not_called()

    @pytest.mark.asyncio
    async def test_merge_new_item_adds_to_user_cart(self, cart_repo):
        product_id = uuid4()
        guest_items = [{"product_id": str(product_id), "quantity": 3}]

        use_case = MergeCartUseCase(cart_repo)
        await use_case.execute("user-1", guest_items)

        cart_repo.add_item.assert_called_once_with("user-1", product_id, 3)

    @pytest.mark.asyncio
    async def test_merge_existing_item_accumulates_quantity(self, cart_repo):
        product_id = uuid4()
        existing = MagicMock()
        existing.quantity = 2
        cart_repo.get_item.return_value = existing

        guest_items = [{"product_id": str(product_id), "quantity": 5}]

        use_case = MergeCartUseCase(cart_repo)
        await use_case.execute("user-1", guest_items)

        cart_repo.update_quantity.assert_called_once_with("user-1", product_id, 7)
        cart_repo.add_item.assert_not_called()

    @pytest.mark.asyncio
    async def test_merge_skips_invalid_quantity(self, cart_repo):
        guest_items = [{"product_id": str(uuid4()), "quantity": 0}]

        use_case = MergeCartUseCase(cart_repo)
        await use_case.execute("user-1", guest_items)

        cart_repo.add_item.assert_not_called()
        cart_repo.update_quantity.assert_not_called()
