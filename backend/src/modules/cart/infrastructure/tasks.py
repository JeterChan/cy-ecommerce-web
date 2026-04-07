"""
Cart Sync Celery Tasks

Background tasks for syncing member cart from Redis to PostgreSQL.
"""

import logging
import asyncio
import uuid
from datetime import datetime, timezone

from infrastructure.celery_app import celery_app
from infrastructure.redis import redis_manager
from infrastructure.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(
    name="modules.cart.infrastructure.tasks.sync_member_cart_task",
    bind=True,
    max_retries=5,
    default_retry_delay=60,  # 1 minute
)
def sync_member_cart_task(self, user_id: str):
    """
    將會員購物車從 Redis 同步至 PostgreSQL

    採用全量 UPSERT 策略：
    1. 從 Redis 讀取該會員所有商品。
    2. 在資料庫中執行 UPSERT (INSERT ... ON CONFLICT DO UPDATE)。
    3. 移除資料庫中不在 Redis 中的項目（確保最終一致性）。
    """
    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(sync_member_cart_logic(user_id, self))
    except Exception as exc:
        # 如果是 Retry 例外，直接拋出
        if isinstance(exc, self.Retry):
            raise exc

        logger.error("❌ 會員 %s 購物車同步失敗：%s", user_id, exc)
        # 指數退避重試
        raise self.retry(exc=exc, countdown=min(60 * (2**self.request.retries), 3600))


async def sync_member_cart_logic(user_id: str, task_instance=None):
    """
    購物車同步邏輯 (Async)
    """
    from sqlalchemy.ext.asyncio import (
        create_async_engine,
        async_sessionmaker,
        AsyncSession,
    )
    from sqlalchemy import select, delete, insert
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    from modules.cart.infrastructure.models import CartModel, CartItemModel
    from modules.cart.infrastructure.repositories.redis_repository import (
        RedisCartRepository,
    )

    # 1. 初始化資源
    engine = create_async_engine(settings.database_url)
    sessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    await redis_manager.connect()
    redis_repo = RedisCartRepository(redis_manager.client)

    # 2. 分散式鎖，確保單一使用者同步串行化
    async with redis_manager.distributed_lock(
        f"cart_sync:{user_id}", expire=30
    ) as acquired:
        if not acquired:
            logger.warning("⚠️ 會員 %s 的同步任務正在進行中，將進行重試", user_id)
            # 鎖定中，拋出 Retry 例外讓 Celery 稍後重試 (1秒後)
            if task_instance:
                raise task_instance.retry(countdown=1)
            else:
                return  # 若無 task instance (例如測試), 則返回

        # 3. 從 Redis 獲取數據
        redis_items = await redis_repo.get_cart(user_id)
        user_uuid = uuid.UUID(user_id)

        async with sessionLocal() as session:
            # 4. 取得或建立購物車 ID
            stmt = select(CartModel).where(CartModel.user_id == user_uuid)
            result = await session.execute(stmt)
            cart = result.scalar_one_or_none()

            if not cart:
                cart = CartModel(user_id=user_uuid)
                session.add(cart)
                await session.flush()

            cart_id = cart.id

            # 5. 執行 UPSERT (PostgreSQL 語法)
            if redis_items:
                # 準備數據
                values = [
                    {
                        "cart_id": cart_id,
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "updated_at": datetime.now(timezone.utc),
                    }
                    for item in redis_items
                ]

                # 執行 INSERT ... ON CONFLICT
                upsert_stmt = pg_insert(CartItemModel).values(values)
                upsert_stmt = upsert_stmt.on_conflict_do_update(
                    index_elements=["cart_id", "product_id"],
                    set_={
                        "quantity": upsert_stmt.excluded.quantity,
                        "updated_at": upsert_stmt.excluded.updated_at,
                    },
                )
                await session.execute(upsert_stmt)

                # 6. 清理不在 Redis 中的項目 (Delete stale items)
                redis_product_ids = [item.product_id for item in redis_items]
                cleanup_stmt = delete(CartItemModel).where(
                    CartItemModel.cart_id == cart_id,
                    CartItemModel.product_id.notin_(redis_product_ids),
                )
                await session.execute(cleanup_stmt)
            else:
                # Redis 為空，清空資料庫
                cleanup_stmt = delete(CartItemModel).where(
                    CartItemModel.cart_id == cart_id
                )
                await session.execute(cleanup_stmt)

            await session.commit()
            logger.info("✅ 會員 %s 購物車同步成功", user_id)

    await engine.dispose()
