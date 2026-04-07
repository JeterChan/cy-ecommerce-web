import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from modules.order.application.use_cases.checkout import CheckoutUseCase
from modules.order.application.use_cases.update_order_status import (
    UpdateOrderStatusUseCase,
)
from modules.order.domain.exceptions import (
    EmptyCartException,
    InsufficientStockException,
)
from modules.order.domain.value_objects import OrderStatus

# ── CheckoutUseCase ──


class TestCheckoutUseCase:
    @pytest.fixture
    def db(self):
        db = AsyncMock()
        db.in_transaction.return_value = False
        return db

    @pytest.fixture
    def order_repo(self):
        return AsyncMock()

    @pytest.fixture
    def cart_repo(self):
        repo = AsyncMock()
        repo.get_cart.return_value = []
        return repo

    @pytest.fixture
    def product_port(self):
        return AsyncMock()

    @pytest.fixture
    def stock_service(self):
        svc = AsyncMock()
        svc.try_deduct.return_value = (True, 5)
        return svc

    @pytest.mark.asyncio
    async def test_empty_cart_raises(
        self, db, order_repo, cart_repo, product_port, stock_service
    ):
        cart_repo.get_cart.return_value = []

        use_case = CheckoutUseCase(
            db, order_repo, cart_repo, product_port, stock_service
        )

        with pytest.raises(EmptyCartException):
            await use_case.execute(uuid4(), MagicMock())

    @pytest.mark.asyncio
    async def test_redis_deduct_failure_rolls_back_previous(
        self, db, order_repo, cart_repo, product_port, stock_service
    ):
        pid1, pid2 = uuid4(), uuid4()
        item1 = MagicMock(product_id=pid1, quantity=2)
        item2 = MagicMock(product_id=pid2, quantity=3)
        cart_repo.get_cart.return_value = [item1, item2]

        # 第一個成功，第二個失敗
        stock_service.try_deduct.side_effect = [(True, 8), (False, 0)]

        use_case = CheckoutUseCase(
            db, order_repo, cart_repo, product_port, stock_service
        )

        with pytest.raises(InsufficientStockException):
            await use_case.execute(uuid4(), MagicMock())

        # 應回滾第一個已預扣的商品
        stock_service.rollback.assert_called_once_with(pid1, 2)

    def test_generate_order_number_format(self):
        """訂單編號為 20 位純數字字串"""
        use_case = CheckoutUseCase.__new__(CheckoutUseCase)
        user_id = uuid4()
        order_number = use_case._generate_order_number(user_id)

        assert len(order_number) == 20
        assert order_number.isdigit()


# ── UpdateOrderStatusUseCase ──


class TestUpdateOrderStatusUseCase:
    @pytest.fixture
    def db(self):
        db = MagicMock()
        # db.begin() must return an async context manager
        cm = AsyncMock()
        cm.__aenter__ = AsyncMock(return_value=None)
        cm.__aexit__ = AsyncMock(return_value=False)
        db.begin.return_value = cm
        return db

    @pytest.fixture
    def order_repo(self):
        return AsyncMock()

    @pytest.fixture
    def product_port(self):
        return AsyncMock()

    def _make_order(self, user_id, status="PENDING"):
        item = MagicMock()
        item.product_id = uuid4()
        item.quantity = 3
        order = MagicMock()
        order.user_id = user_id
        order.status = status
        order.items = [item]
        return order

    @pytest.mark.asyncio
    async def test_non_owner_rejected(self, db, order_repo, product_port):
        owner_id = uuid4()
        other_id = uuid4()
        order = self._make_order(owner_id)
        order_repo.get_by_id.return_value = order

        use_case = UpdateOrderStatusUseCase(db, order_repo, product_port)

        with pytest.raises(ValueError, match="無權操作此訂單"):
            await use_case.execute(uuid4(), other_id, "CANCELLED")

    @pytest.mark.asyncio
    async def test_cancel_order_restores_stock(self, db, order_repo, product_port):
        user_id = uuid4()
        order = self._make_order(user_id, status=OrderStatus.PENDING.value)
        order_repo.get_by_id.return_value = order
        order_repo.update.return_value = order

        use_case = UpdateOrderStatusUseCase(db, order_repo, product_port)
        await use_case.execute(uuid4(), user_id, "CANCELLED")

        product_port.restore_stock.assert_called_once_with(
            order.items[0].product_id, order.items[0].quantity
        )

    @pytest.mark.asyncio
    async def test_order_not_found_raises(self, db, order_repo, product_port):
        order_repo.get_by_id.return_value = None

        use_case = UpdateOrderStatusUseCase(db, order_repo, product_port)

        with pytest.raises(ValueError, match="訂單不存在"):
            await use_case.execute(uuid4(), uuid4(), "CANCELLED")
