"""
測試 product route handler 的快取行為

驗證 route handler 層的 Cache-Aside 讀取與 Write-Invalidate 寫入失效邏輯。
使用 mock 避免真實 DB/Redis 連線。
"""

import json
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from redis.exceptions import ConnectionError as RedisConnectionError

from infrastructure.product_cache_service import (
    ProductCacheService,
    DETAIL_PREFIX,
)

# ── 商品詳情快取整合 ──


class TestGetProductCacheIntegration:
    """驗證 get_product handler 的快取行為"""

    @pytest.mark.asyncio
    async def test_cache_hit_skips_db(self):
        """cache hit 時不應呼叫 use case"""
        product_id = uuid4()
        cached_data = {
            "id": str(product_id),
            "name": "Cached Product",
            "price": "100.00",
            "stock_quantity": 10,
            "is_active": True,
            "images": [],
            "category_id": None,
            "category_name": None,
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-01T00:00:00",
        }

        redis = AsyncMock()
        redis.get.return_value = json.dumps(cached_data)

        cache_service = ProductCacheService(redis)
        result = await cache_service.get_product_detail(product_id)

        assert result is not None
        assert result["name"] == "Cached Product"
        redis.get.assert_called_once_with(f"{DETAIL_PREFIX}{product_id}")

    @pytest.mark.asyncio
    async def test_cache_miss_returns_none(self):
        """cache miss 時回傳 None，讓 handler 查 DB"""
        redis = AsyncMock()
        redis.get.return_value = None

        cache_service = ProductCacheService(redis)
        result = await cache_service.get_product_detail(uuid4())

        assert result is None


# ── 商品列表快取整合 ──


class TestListProductsCacheIntegration:
    """驗證 list_products handler 的快取行為"""

    @pytest.mark.asyncio
    async def test_same_params_produce_same_cache_key(self):
        """相同查詢參數應產生相同的 cache key"""
        key1 = ProductCacheService.build_list_cache_key(
            skip=0, limit=10, category_id=1, is_active=True
        )
        key2 = ProductCacheService.build_list_cache_key(
            skip=0, limit=10, category_id=1, is_active=True
        )
        assert key1 == key2

    @pytest.mark.asyncio
    async def test_list_cache_hit(self):
        """列表快取命中時回傳快取資料"""
        cache_key = ProductCacheService.build_list_cache_key(skip=0, limit=10)
        cached_data = {"items": [], "total": 0, "skip": 0, "limit": 10}

        redis = AsyncMock()
        redis.get.return_value = json.dumps(cached_data)

        cache_service = ProductCacheService(redis)
        result = await cache_service.get_product_list(cache_key)

        assert result is not None
        assert result["total"] == 0


# ── 寫入失效 ──


class TestWriteInvalidation:
    """驗證各寫入操作後的快取失效行為"""

    @pytest.mark.asyncio
    async def test_update_invalidates_detail_and_lists(self):
        """更新商品後應刪除詳情快取和所有列表快取"""
        product_id = uuid4()
        redis = AsyncMock()
        redis.scan.side_effect = [(0, [b"product:list:abc"])]

        cache_service = ProductCacheService(redis)
        await cache_service.invalidate_product_detail(product_id)
        await cache_service.invalidate_all_product_lists()

        redis.delete.assert_any_call(f"{DETAIL_PREFIX}{product_id}")
        redis.delete.assert_any_call(b"product:list:abc")

    @pytest.mark.asyncio
    async def test_create_invalidates_only_lists(self):
        """新增商品後只需刪除列表快取"""
        redis = AsyncMock()
        redis.scan.side_effect = [(0, [b"product:list:a", b"product:list:b"])]

        cache_service = ProductCacheService(redis)
        await cache_service.invalidate_all_product_lists()

        # 應刪除所有列表快取
        redis.delete.assert_called_once_with(b"product:list:a", b"product:list:b")

    @pytest.mark.asyncio
    async def test_adjust_stock_invalidates_only_detail(self):
        """調整庫存後只需刪除詳情快取"""
        product_id = uuid4()
        redis = AsyncMock()

        cache_service = ProductCacheService(redis)
        await cache_service.invalidate_product_detail(product_id)

        redis.delete.assert_called_once_with(f"{DETAIL_PREFIX}{product_id}")


# ── Redis 降級 ──


class TestRedisFallback:
    """驗證 Redis 不可用時的降級行為"""

    @pytest.mark.asyncio
    async def test_get_detail_fallback_on_error(self):
        """Redis 異常時 get 回傳 None，不影響流程"""
        redis = AsyncMock()
        redis.get.side_effect = RedisConnectionError("down")

        cache_service = ProductCacheService(redis)
        result = await cache_service.get_product_detail(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_set_detail_fallback_on_error(self):
        """Redis 異常時 set 不拋錯"""
        redis = AsyncMock()
        redis.set.side_effect = RedisConnectionError("down")

        cache_service = ProductCacheService(redis)
        await cache_service.set_product_detail(uuid4(), {"name": "test"})

    @pytest.mark.asyncio
    async def test_invalidate_lists_fallback_on_error(self):
        """Redis 異常時 invalidate 不拋錯"""
        redis = AsyncMock()
        redis.scan.side_effect = RedisConnectionError("down")

        cache_service = ProductCacheService(redis)
        await cache_service.invalidate_all_product_lists()
