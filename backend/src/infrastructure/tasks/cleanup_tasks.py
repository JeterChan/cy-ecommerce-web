"""
帳戶清理 Celery 任務

每日執行：永久刪除超過 30 天的軟刪除帳戶。
"""

import logging
from datetime import datetime, timezone, timedelta

from infrastructure.celery_app import celery_app

logger = logging.getLogger(__name__)

HARD_DELETE_AFTER_DAYS = 30


@celery_app.task(
    name="infrastructure.tasks.cleanup_tasks.hard_delete_expired_accounts",
)
def hard_delete_expired_accounts() -> dict:
    """
    永久刪除已軟刪除超過 30 天的帳戶

    此任務由 Celery Beat 每日排程執行（00:00 Asia/Taipei）。

    Returns:
        dict: 包含 deleted_count 的執行結果
    """
    import asyncio
    from sqlalchemy import delete as sa_delete
    from sqlalchemy.ext.asyncio import (
        create_async_engine,
        async_sessionmaker,
        AsyncSession,
    )
    from infrastructure.config import settings
    from modules.auth.infrastructure.models import UserModel

    async def _run() -> int:
        cutoff_date = datetime.now(timezone.utc) - timedelta(
            days=HARD_DELETE_AFTER_DAYS
        )

        engine = create_async_engine(settings.database_url)
        SessionLocal = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        async with SessionLocal() as session:
            stmt = sa_delete(UserModel).where(
                UserModel.deleted_at.isnot(None),
                UserModel.deleted_at < cutoff_date,
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount

        await engine.dispose()

    try:
        deleted_count = asyncio.run(_run())
        logger.info("✅ 硬刪除完成：共刪除 %d 個過期帳戶", deleted_count)
        return {"deleted_count": deleted_count}
    except Exception as exc:
        logger.error("❌ 硬刪除失敗：%s", exc)
        raise
