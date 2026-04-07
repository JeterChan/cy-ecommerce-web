import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from infrastructure.stock_redis_service import StockRedisService


@pytest.fixture
def redis():
    return AsyncMock()


@pytest.fixture
def db():
    return AsyncMock()


@pytest.fixture
def service(redis, db):
    return StockRedisService(redis=redis, db=db)


# ── try_deduct ──


class TestTryDeduct:
    @pytest.mark.asyncio
    async def test_stock_sufficient_returns_true(self, service, redis):
        redis.exists.return_value = 1
        redis.decrby.return_value = 5  # 剩餘 5

        success, remaining = await service.try_deduct(uuid4(), 3)

        assert success is True
        assert remaining == 5

    @pytest.mark.asyncio
    async def test_stock_insufficient_rolls_back(self, service, redis):
        redis.exists.return_value = 1
        redis.decrby.return_value = -2  # 不夠

        product_id = uuid4()
        success, remaining = await service.try_deduct(product_id, 5)

        assert success is False
        assert remaining == 0
        redis.incrby.assert_called_once_with(f"stock:{product_id}", 5)

    @pytest.mark.asyncio
    async def test_key_not_exists_lazy_init_and_retry_success(self, service, redis, db):
        product_id = uuid4()
        redis.exists.return_value = 0
        # 第一次 decrby 回傳 -3（key 不存在，從 0 開始扣）
        # 重試 decrby 回傳 7（載入 10，扣 3）
        redis.decrby.side_effect = [-3, 7]

        # Mock _load_stock_from_db
        with patch.object(service, "_load_stock_from_db", return_value=10) as mock_load:
            success, remaining = await service.try_deduct(product_id, 3)

        assert success is True
        assert remaining == 7
        # 應先回滾 incrby，再 delete，再 set，再 decrby
        redis.delete.assert_called_once()
        redis.set.assert_called_once_with(f"stock:{product_id}", 10)

    @pytest.mark.asyncio
    async def test_key_not_exists_lazy_init_still_insufficient(
        self, service, redis, db
    ):
        product_id = uuid4()
        redis.exists.return_value = 0
        # 第一次 decrby: -5，重試 decrby: -2（載入 3，扣 5）
        redis.decrby.side_effect = [-5, -2]

        with patch.object(service, "_load_stock_from_db", return_value=3):
            success, remaining = await service.try_deduct(product_id, 5)

        assert success is False
        assert remaining == 0
        # 重試失敗也要回滾
        assert redis.incrby.call_count == 2  # 第一次回滾 + 重試後回滾


# ── rollback ──


class TestRollback:
    @pytest.mark.asyncio
    async def test_rollback_calls_incrby(self, service, redis):
        product_id = uuid4()
        await service.rollback(product_id, 7)

        redis.incrby.assert_called_once_with(f"stock:{product_id}", 7)


# ── sync_stock ──


class TestSyncStock:
    @pytest.mark.asyncio
    async def test_key_exists_uses_incrby(self, service, redis):
        product_id = uuid4()
        redis.exists.return_value = 1

        await service.sync_stock(product_id, 5)

        redis.incrby.assert_called_once_with(f"stock:{product_id}", 5)

    @pytest.mark.asyncio
    async def test_key_not_exists_loads_from_db(self, service, redis):
        product_id = uuid4()
        redis.exists.return_value = 0

        with patch.object(service, "_load_stock_from_db", return_value=42):
            await service.sync_stock(product_id, 5)

        redis.set.assert_called_once_with(f"stock:{product_id}", 42)
        redis.incrby.assert_not_called()
