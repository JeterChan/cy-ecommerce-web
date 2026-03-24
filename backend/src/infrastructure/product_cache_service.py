"""
商品資訊 Redis 快取服務

使用 Cache-Aside + Write-Invalidate 策略：
- 讀取：先查 Redis，cache miss 時由呼叫端查 DB 並回寫快取
- 寫入：管理員操作後主動刪除（invalidate）對應 key

Key patterns:
- product:detail:{product_id}  — 商品詳情，TTL 30 分鐘
- product:list:{params_hash}   — 商品列表，TTL 10 分鐘
"""
import hashlib
import json
import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple

from redis.asyncio import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

DETAIL_TTL = 60 * 30  # 30 分鐘
LIST_TTL = 60 * 10    # 10 分鐘

DETAIL_PREFIX = "product:detail:"
LIST_PREFIX = "product:list:"


class ProductCacheService:

    def __init__(self, redis: Optional[Redis]):
        self.redis = redis

    # ------------------------------------------------------------------
    # 商品詳情快取
    # ------------------------------------------------------------------

    async def get_product_detail(self, product_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """從 Redis 讀取商品詳情 JSON，cache miss 或 Redis 不可用時回傳 None"""
        if self.redis is None:
            return None
        try:
            data = await self.redis.get(f"{DETAIL_PREFIX}{product_id}")
        except RedisError:
            logger.warning("Redis get_product_detail failed for %s", product_id, exc_info=True)
            return None
        if data is None:
            return None
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            logger.error("JSON decode failed in get_product_detail for %s", product_id, exc_info=True)
            try:
                await self.redis.delete(f"{DETAIL_PREFIX}{product_id}")
            except RedisError:
                logger.warning("Redis delete failed during decode recovery for %s", product_id, exc_info=True)
            return None

    async def set_product_detail(self, product_id: uuid.UUID, dto_dict: Dict[str, Any]) -> None:
        """將商品詳情寫入 Redis，TTL 30 分鐘；Redis 不可用時靜默跳過"""
        if self.redis is None:
            return
        payload = json.dumps(dto_dict, default=str)
        try:
            await self.redis.set(
                f"{DETAIL_PREFIX}{product_id}",
                payload,
                ex=DETAIL_TTL,
            )
        except RedisError:
            logger.warning("Redis set_product_detail failed for %s", product_id, exc_info=True)

    async def invalidate_product_detail(self, product_id: uuid.UUID) -> None:
        """刪除指定商品的詳情快取；Redis 不可用時靜默跳過"""
        if self.redis is None:
            return
        try:
            await self.redis.delete(f"{DETAIL_PREFIX}{product_id}")
        except RedisError:
            logger.warning("Redis invalidate_product_detail failed for %s", product_id, exc_info=True)

    # ------------------------------------------------------------------
    # 商品列表快取
    # ------------------------------------------------------------------

    @staticmethod
    def build_list_cache_key(**params: Any) -> str:
        """將查詢參數排序後做 SHA256 hash 產生 cache key"""
        sorted_items = sorted(
            ((k, v) for k, v in params.items() if v is not None),
            key=lambda x: x[0],
        )
        raw = json.dumps(sorted_items, default=str)
        digest = hashlib.sha256(raw.encode()).hexdigest()
        return f"{LIST_PREFIX}{digest}"

    async def get_product_list(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """從 Redis 讀取商品列表 JSON，cache miss 或 Redis 不可用時回傳 None"""
        if self.redis is None:
            return None
        try:
            data = await self.redis.get(cache_key)
        except RedisError:
            logger.warning("Redis get_product_list failed for %s", cache_key, exc_info=True)
            return None
        if data is None:
            return None
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            logger.error("JSON decode failed in get_product_list for %s", cache_key, exc_info=True)
            try:
                await self.redis.delete(cache_key)
            except RedisError:
                logger.warning("Redis delete failed during decode recovery for %s", cache_key, exc_info=True)
            return None

    async def set_product_list(self, cache_key: str, data: Dict[str, Any]) -> None:
        """將商品列表結果寫入 Redis，TTL 10 分鐘；Redis 不可用時靜默跳過"""
        if self.redis is None:
            return
        payload = json.dumps(data, default=str)
        try:
            await self.redis.set(
                cache_key,
                payload,
                ex=LIST_TTL,
            )
        except RedisError:
            logger.warning("Redis set_product_list failed for %s", cache_key, exc_info=True)

    async def invalidate_all_product_lists(self) -> None:
        """使用 SCAN 刪除所有 product:list:* 的 key；Redis 不可用時靜默跳過"""
        if self.redis is None:
            return
        try:
            cursor = 0
            while True:
                cursor, keys = await self.redis.scan(cursor, match=f"{LIST_PREFIX}*", count=100)
                if keys:
                    await self.redis.delete(*keys)
                if cursor == 0:
                    break
        except RedisError:
            logger.warning("Redis invalidate_all_product_lists failed", exc_info=True)
