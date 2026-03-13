from redis.asyncio import Redis, from_url
from src.infrastructure.config import settings
from typing import AsyncGenerator

class RedisClient:
    def __init__(self):
        self._redis: Redis | None = None

    async def connect(self):
        """Initialize the Redis connection."""
        if self._redis is None:
            redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
            if settings.REDIS_PASSWORD:
                redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
            
            self._redis = from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True
            )

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

# Global instance
redis_manager = RedisClient()

async def get_redis() -> AsyncGenerator[Redis, None]:
    """Dependency injection for Redis."""
    yield redis_manager.client
