from redis.asyncio import Redis, from_url
from infrastructure.config import settings
from typing import AsyncGenerator
import time
from contextlib import asynccontextmanager


class RedisClient:
    def __init__(self):
        self._redis: Redis | None = None

    async def connect(self):
        """Initialize the Redis connection."""
        if self._redis is None:
            redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
            if settings.REDIS_PASSWORD:
                redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"

            self._redis = from_url(redis_url, encoding="utf-8", decode_responses=True)

    async def close(self):
        """Close the Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None

    @property
    def client(self) -> Redis:
        """Get the Redis client."""
        if self._redis is None:
            raise RuntimeError("RedisClient not connected. Call connect() first.")
        return self._redis

    @asynccontextmanager
    async def distributed_lock(self, lock_name: str, expire: int = 10):
        """
        簡易的分散式鎖實作 (Context Manager)

        Args:
            lock_name: 鎖的名稱
            expire: 過期時間 (秒)
        """
        redis = self.client
        lock_key = f"lock:{lock_name}"

        # 嘗試獲取鎖 (NX: 只在 key 不存在時設定, EX: 設定過期時間)
        acquired = await redis.set(lock_key, "locked", nx=True, ex=expire)

        try:
            yield acquired
        finally:
            if acquired:
                # 釋放鎖
                await redis.delete(lock_key)


# Global instance
redis_manager = RedisClient()


async def get_redis() -> AsyncGenerator[Redis, None]:
    """Dependency injection for Redis."""
    yield redis_manager.client
