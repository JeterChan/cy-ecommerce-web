"""
Redis 庫存預扣服務

使用 Redis DECRBY 原子操作在 DB 事務之前過濾庫存不足的請求。
Key pattern: stock:{product_id}，value 為整數庫存量。
"""
import uuid
import logging
from typing import Tuple, Optional

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from modules.product.infrastructure.models import ProductModel

logger = logging.getLogger(__name__)


class StockRedisService:

    def __init__(self, redis: Redis, db: Optional[AsyncSession] = None):
        self.redis = redis
        self.db = db

    def _key(self, product_id: uuid.UUID) -> str:
        return f"stock:{product_id}"

    async def init_stock(self, product_id: uuid.UUID, quantity: int) -> None:
        """初始化或覆寫 Redis 庫存（商品建立/完整同步時使用）"""
        await self.redis.set(self._key(product_id), quantity)

    async def get_stock(self, product_id: uuid.UUID) -> Optional[int]:
        """取得 Redis 庫存，key 不存在回傳 None"""
        val = await self.redis.get(self._key(product_id))
        return int(val) if val is not None else None

    async def try_deduct(self, product_id: uuid.UUID, quantity: int) -> Tuple[bool, int]:
        """
        原子預扣庫存。

        Returns:
            (True, remaining)  — 預扣成功
            (False, 0)         — 庫存不足（已自動回滾）
        """
        key = self._key(product_id)

        remaining = await self.redis.decrby(key, quantity)

        if remaining >= 0:
            return True, remaining

        # 結果 < 0：庫存不足，回滾
        await self.redis.incrby(key, quantity)

        # 檢查是否因 key 不存在而回傳負數（lazy init）
        exists = await self.redis.exists(key)
        if exists:
            # key 存在但庫存確實不足
            return False, 0

        # key 不存在 → 從 DB 載入庫存後重試一次
        if self.db is not None:
            loaded = await self._load_stock_from_db(product_id)
            if loaded is not None:
                await self.redis.set(key, loaded)
                logger.info(f"Lazy init stock:{product_id} = {loaded}")
                # 重試扣減
                remaining = await self.redis.decrby(key, quantity)
                if remaining >= 0:
                    return True, remaining
                # 仍然不足，回滾
                await self.redis.incrby(key, quantity)
                return False, 0

        return False, 0

    async def rollback(self, product_id: uuid.UUID, quantity: int) -> None:
        """回滾預扣的庫存（DB 事務失敗時呼叫）"""
        await self.redis.incrby(self._key(product_id), quantity)

    async def sync_stock(self, product_id: uuid.UUID, delta: int) -> None:
        """同步庫存變更（Admin 調整庫存時使用）"""
        key = self._key(product_id)
        exists = await self.redis.exists(key)
        if exists:
            await self.redis.incrby(key, delta)
        else:
            # key 不存在，直接從 DB 載入最新值
            if self.db is not None:
                loaded = await self._load_stock_from_db(product_id)
                if loaded is not None:
                    await self.redis.set(key, loaded)

    async def _load_stock_from_db(self, product_id: uuid.UUID) -> Optional[int]:
        """從 DB 讀取庫存（用於 lazy init）"""
        if self.db is None:
            return None
        result = await self.db.execute(
            select(ProductModel.stock_quantity).where(ProductModel.id == product_id)
        )
        row = result.scalar_one_or_none()
        return row if row is not None else None
