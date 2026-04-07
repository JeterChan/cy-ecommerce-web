"""
Auth Module - Cart Merge Adapter

橋接 Cart 模組的 CartMergeService，
實作 Auth 模組的 ICartMergePort 介面。
"""

import logging
from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from modules.auth.domain.ports import ICartMergePort
from modules.cart.application.services import CartMergeService
from modules.cart.infrastructure.utils import get_guest_token_from_cookie

logger = logging.getLogger(__name__)


class CartMergeAdapter(ICartMergePort):
    """
    購物車合併適配器

    將 Cart 模組的 CartMergeService 和 guest token 工具
    封裝為 Auth 模組的 ICartMergePort 介面。
    """

    def __init__(self, db: AsyncSession, redis: Redis):
        self._db = db
        self._redis = redis

    async def merge_guest_cart(self, request: Request, user_id: UUID) -> None:
        """合併訪客購物車，失敗時僅記錄日誌不中斷流程"""
        try:
            guest_token = get_guest_token_from_cookie(request)
            if guest_token:
                merge_service = CartMergeService(self._db, self._redis)
                await merge_service.merge_guest_to_member(
                    guest_token=guest_token, user_id=user_id
                )
        except Exception as e:
            logger.warning(f"Cart merge failed: {e}")
