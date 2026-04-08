"""
內部 API — 僅供 Cloud Scheduler 等內部服務呼叫
"""

import logging
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy import delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.config import settings
from infrastructure.database import get_db
from modules.auth.infrastructure.models import UserModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/internal", tags=["Internal"])

HARD_DELETE_AFTER_DAYS = 30


def verify_cleanup_api_key(
    x_cleanup_api_key: str = Header(..., alias="X-Cleanup-Api-Key"),
) -> None:
    if not settings.CLEANUP_API_KEY:
        raise HTTPException(status_code=503, detail="Cleanup API not configured")
    if x_cleanup_api_key != settings.CLEANUP_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


@router.post("/cleanup/expired-accounts")
async def cleanup_expired_accounts(
    _: None = Depends(verify_cleanup_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    永久刪除已軟刪除超過 30 天的帳戶。
    由 Cloud Scheduler 每月 1 日 00:00 (Asia/Taipei) 呼叫。
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=HARD_DELETE_AFTER_DAYS)

    stmt = sa_delete(UserModel).where(
        UserModel.deleted_at.isnot(None),
        UserModel.deleted_at < cutoff_date,
    )
    result = await db.execute(stmt)
    deleted_count = result.rowcount

    logger.info("硬刪除完成：共刪除 %d 個過期帳戶", deleted_count)
    return {"deleted_count": deleted_count}
