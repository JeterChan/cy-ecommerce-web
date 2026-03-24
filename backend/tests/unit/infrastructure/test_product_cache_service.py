import json
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from infrastructure.product_cache_service import (
    ProductCacheService,
    DETAIL_PREFIX,
    DETAIL_TTL,
    LIST_PREFIX,
    LIST_TTL,
)


@pytest.fixture
def redis():
    return AsyncMock()


@pytest.fixture
def service(redis):
    return ProductCacheService(redis=redis)


# ── get_product_detail ──


class TestGetProductDetail:
    @pytest.mark.asyncio
    async def test_cache_hit(self, service, redis):
        product_id = uuid4()
        expected = {"id": str(product_id), "name": "Test"}
        redis.get.return_value = json.dumps(expected)

        result = await service.get_product_detail(product_id)

        assert result == expected
        redis.get.assert_called_once_with(f"{DETAIL_PREFIX}{product_id}")

    @pytest.mark.asyncio
    async def test_cache_miss(self, service, redis):
        redis.get.return_value = None

        result = await service.get_product_detail(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_redis_error_returns_none(self, service, redis):
        redis.get.side_effect = ConnectionError("Redis down")

        result = await service.get_product_detail(uuid4())

        assert result is None


# ── set_product_detail ──


class TestSetProductDetail:
    @pytest.mark.asyncio
    async def test_writes_json_with_ttl(self, service, redis):
        product_id = uuid4()
        data = {"id": str(product_id), "name": "Test"}

        await service.set_product_detail(product_id, data)

        redis.set.assert_called_once_with(
            f"{DETAIL_PREFIX}{product_id}",
            json.dumps(data, default=str),
            ex=DETAIL_TTL,
        )

    @pytest.mark.asyncio
    async def test_redis_error_does_not_raise(self, service, redis):
        redis.set.side_effect = ConnectionError("Redis down")

        await service.set_product_detail(uuid4(), {"name": "Test"})
        # Should not raise


# ── invalidate_product_detail ──


class TestInvalidateProductDetail:
    @pytest.mark.asyncio
    async def test_deletes_key(self, service, redis):
        product_id = uuid4()

        await service.invalidate_product_detail(product_id)

        redis.delete.assert_called_once_with(f"{DETAIL_PREFIX}{product_id}")

    @pytest.mark.asyncio
    async def test_redis_error_does_not_raise(self, service, redis):
        redis.delete.side_effect = ConnectionError("Redis down")

        await service.invalidate_product_detail(uuid4())


# ── build_list_cache_key ──


class TestBuildListCacheKey:
    def test_returns_prefixed_hash(self):
        key = ProductCacheService.build_list_cache_key(skip=0, limit=10)

        assert key.startswith(LIST_PREFIX)

    def test_same_params_same_key(self):
        key1 = ProductCacheService.build_list_cache_key(skip=0, limit=10, category_id=1)
        key2 = ProductCacheService.build_list_cache_key(skip=0, limit=10, category_id=1)

        assert key1 == key2

    def test_different_params_different_key(self):
        key1 = ProductCacheService.build_list_cache_key(skip=0, limit=10)
        key2 = ProductCacheService.build_list_cache_key(skip=0, limit=20)

        assert key1 != key2

    def test_param_order_does_not_matter(self):
        key1 = ProductCacheService.build_list_cache_key(skip=0, limit=10, category_id=1)
        key2 = ProductCacheService.build_list_cache_key(category_id=1, limit=10, skip=0)

        assert key1 == key2

    def test_none_params_are_excluded(self):
        key1 = ProductCacheService.build_list_cache_key(skip=0, limit=10)
        key2 = ProductCacheService.build_list_cache_key(skip=0, limit=10, category_id=None)

        assert key1 == key2


# ── get_product_list / set_product_list ──


class TestProductListCache:
    @pytest.mark.asyncio
    async def test_get_cache_hit(self, service, redis):
        cache_key = f"{LIST_PREFIX}abc123"
        expected = {"items": [], "total": 0}
        redis.get.return_value = json.dumps(expected)

        result = await service.get_product_list(cache_key)

        assert result == expected

    @pytest.mark.asyncio
    async def test_get_cache_miss(self, service, redis):
        redis.get.return_value = None

        result = await service.get_product_list(f"{LIST_PREFIX}missing")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_redis_error_returns_none(self, service, redis):
        redis.get.side_effect = ConnectionError("Redis down")

        result = await service.get_product_list(f"{LIST_PREFIX}key")

        assert result is None

    @pytest.mark.asyncio
    async def test_set_writes_json_with_ttl(self, service, redis):
        cache_key = f"{LIST_PREFIX}abc123"
        data = {"items": [], "total": 0}

        await service.set_product_list(cache_key, data)

        redis.set.assert_called_once_with(
            cache_key,
            json.dumps(data, default=str),
            ex=LIST_TTL,
        )

    @pytest.mark.asyncio
    async def test_set_redis_error_does_not_raise(self, service, redis):
        redis.set.side_effect = ConnectionError("Redis down")

        await service.set_product_list(f"{LIST_PREFIX}key", {"items": []})


# ── invalidate_all_product_lists ──


class TestInvalidateAllProductLists:
    @pytest.mark.asyncio
    async def test_scans_and_deletes_keys(self, service, redis):
        keys = [b"product:list:a", b"product:list:b"]
        redis.scan.side_effect = [(0, keys)]

        await service.invalidate_all_product_lists()

        redis.scan.assert_called_once_with(0, match=f"{LIST_PREFIX}*", count=100)
        redis.delete.assert_called_once_with(*keys)

    @pytest.mark.asyncio
    async def test_handles_multiple_scan_iterations(self, service, redis):
        keys1 = [b"product:list:a"]
        keys2 = [b"product:list:b"]
        redis.scan.side_effect = [(42, keys1), (0, keys2)]

        await service.invalidate_all_product_lists()

        assert redis.scan.call_count == 2
        assert redis.delete.call_count == 2

    @pytest.mark.asyncio
    async def test_no_keys_to_delete(self, service, redis):
        redis.scan.side_effect = [(0, [])]

        await service.invalidate_all_product_lists()

        redis.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_redis_error_does_not_raise(self, service, redis):
        redis.scan.side_effect = ConnectionError("Redis down")

        await service.invalidate_all_product_lists()
