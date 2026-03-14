"""
Hybrid Cart Repository Implementation

This module implements a hybrid storage strategy for member carts:
- Write-Behind: Writes to Redis immediately and syncs to PostgreSQL asynchronously.
- Read-Fallback: Reads from Redis primarily, falls back to PostgreSQL on cache miss.
"""

from typing import List, Optional
import uuid
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from modules.cart.domain.repository import ICartRepository
from modules.cart.domain.entities import CartItemResponse, CartItemCreate
from modules.cart.infrastructure.repositories.redis_repository import RedisCartRepository
from modules.cart.infrastructure.repositories.sql_repository import SQLCartRepository


class HybridCartRepository(ICartRepository):
    """會員購物車的混合儲存實作 (Redis + PostgreSQL 非同步同步)"""

    def __init__(self, redis_client: Redis, db_session: AsyncSession):
        """
        初始化 Hybrid Cart Repository

        Args:
            redis_client: Redis async client
            db_session: SQLAlchemy AsyncSession
        """
        self.redis_repo = RedisCartRepository(redis_client)
        self.sql_repo = SQLCartRepository(db_session)
        self.db = db_session

    def _trigger_sync(self, user_id: str):
        """
        觸發非同步同步任務 (Celery)
        
        Note: 延遲匯入以避免循環依賴
        """
        from modules.cart.infrastructure.tasks import sync_member_cart_task
        sync_member_cart_task.apply_async(args=[user_id], queue='cart_sync_queue')

    async def add_item(
        self,
        owner_id: str,
        product_id: uuid.UUID,
        quantity: int
    ) -> CartItemResponse:
        """立即更新 Redis 並觸發同步任務"""
        # 1. 寫入 Redis
        result = await self.redis_repo.add_item(owner_id, product_id, quantity)
        
        # 2. 觸發同步
        self._trigger_sync(owner_id)
        
        return result

    async def update_quantity(
        self,
        owner_id: str,
        product_id: uuid.UUID,
        quantity: int
    ) -> CartItemResponse:
        """立即更新 Redis 並觸發同步任務"""
        result = await self.redis_repo.update_quantity(owner_id, product_id, quantity)
        self._trigger_sync(owner_id)
        return result

    async def remove_item(
        self,
        owner_id: str,
        product_id: uuid.UUID
    ) -> None:
        """從 Redis 移除並觸發同步任務"""
        await self.redis_repo.remove_item(owner_id, product_id)
        self._trigger_sync(owner_id)

    async def clear_cart(
        self,
        owner_id: str
    ) -> None:
        """清空 Redis 並觸發同步任務"""
        await self.redis_repo.clear_cart(owner_id)
        self._trigger_sync(owner_id)

    async def get_cart(
        self,
        owner_id: str
    ) -> List[CartItemResponse]:
        """優先從 Redis 讀取，若為空則從 SQL 讀取並回填"""
        # 1. 嘗試從 Redis 讀取
        items = await self.redis_repo.get_cart(owner_id)
        
        if not items:
            # 2. Redis 為空，從 PostgreSQL 讀取
            items = await self.sql_repo.get_cart(owner_id)
            
            if items:
                # 3. 回填 Redis (使用批量寫入避免 N+1 問題)
                # 將 CartItemResponse 轉換為 CartItemCreate 格式
                items_to_create = [
                    CartItemCreate(
                        product_id=item.product_id,
                        quantity=item.quantity
                    )
                    for item in items
                ]
                await self.redis_repo.batch_add_items(owner_id, items_to_create)
        
        return items

    async def get_item(
        self,
        owner_id: str,
        product_id: uuid.UUID
    ) -> Optional[CartItemResponse]:
        """優先從 Redis 讀取，若缺失則從 SQL 讀取並回填"""
        item = await self.redis_repo.get_item(owner_id, product_id)
        
        if not item:
            item = await self.sql_repo.get_item(owner_id, product_id)
            if item:
                # 回填單一項目
                await self.redis_repo.add_item(owner_id, product_id, item.quantity)

        return item

    async def batch_add_items(
        self,
        owner_id: str,
        items: List[CartItemCreate]
    ) -> List[CartItemResponse]:
        """批量操作：更新 Redis 並觸發單次同步任務"""
        results = await self.redis_repo.batch_add_items(owner_id, items)
        self._trigger_sync(owner_id)
        return results
