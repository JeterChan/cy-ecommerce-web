"""
Cart Merge Service

處理訪客購物車合併到會員購物車的業務邏輯

使用場景：
- 訪客瀏覽商品並加入購物車（儲存在 Redis）
- 訪客登入成為會員
- 系統自動將訪客購物車合併到會員購物車（PostgreSQL）
- 清除訪客購物車
"""

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from modules.cart.infrastructure.repositories.redis_repository import (
    RedisCartRepository,
)
from modules.cart.infrastructure.repositories.sql_repository import SQLCartRepository
from modules.cart.domain.entities import CartItemCreate


class CartMergeService:
    """
    購物車合併服務

    職責：
    - 從 Redis 讀取訪客購物車
    - 合併到會員購物車（PostgreSQL）
    - 處理重複商品（數量累加）
    - 清除訪客購物車
    - 錯誤隔離（不影響登入流程）
    """

    def __init__(self, db: AsyncSession, redis: Redis):
        """
        初始化合併服務

        Args:
            db: SQLAlchemy AsyncSession
            redis: Redis async client
        """
        self.db = db
        self.redis = redis
        self.redis_repo = RedisCartRepository(redis)
        self.sql_repo = SQLCartRepository(db)

    async def merge_guest_to_member(self, guest_token: str, user_id: uuid.UUID) -> dict:
        """
        將訪客購物車合併到會員購物車

        合併邏輯：
        1. 從 Redis 讀取訪客購物車項目
        2. 若訪客購物車為空，直接返回
        3. 將每個項目加入會員購物車
           - 相同商品 → 數量累加（由 SQLCartRepository.add_item 處理）
           - 不同商品 → 新增項目
        4. 清除訪客購物車（Redis）
        5. 返回合併結果

        Args:
            guest_token: 訪客識別碼
            user_id: 會員 UUID

        Returns:
            dict: 合併結果統計
            {
                "success": True/False,
                "merged_items": 3,  # 成功合併的商品種類數
                "total_quantity": 5,  # 合併的總數量
                "errors": []  # 錯誤訊息列表（若有）
            }
        """
        result = {
            "success": False,
            "merged_items": 0,
            "total_quantity": 0,
            "errors": [],
        }

        try:
            # 1. 讀取訪客購物車
            guest_items = await self.redis_repo.get_cart(guest_token)

            if not guest_items:
                # 訪客購物車為空，直接成功
                result["success"] = True
                return result

            # 2. 準備批量新增的資料
            items_to_merge = [
                CartItemCreate(product_id=item.product_id, quantity=item.quantity)
                for item in guest_items
            ]

            # 3. 批量合併到會員購物車
            # SQLCartRepository.batch_add_items 會自動處理重複商品（數量累加）
            owner_id = str(user_id)
            merged_items = await self.sql_repo.batch_add_items(
                owner_id=owner_id, items=items_to_merge
            )

            # 4. 統計結果
            result["merged_items"] = len(merged_items)
            result["total_quantity"] = sum(item.quantity for item in merged_items)

            # 5. 清除訪客購物車
            await self.redis_repo.clear_cart(guest_token)

            # 6. Commit transaction
            await self.db.commit()

            result["success"] = True

        except Exception as e:
            # 錯誤處理：Rollback transaction
            await self.db.rollback()
            result["errors"].append(str(e))
            # 注意：錯誤不應中斷登入流程，只返回錯誤資訊

        return result

    async def get_merge_preview(self, guest_token: str, user_id: uuid.UUID) -> dict:
        """
        預覽合併結果（不實際執行）

        用於在登入前顯示給使用者：
        "您有 3 件商品將會合併到購物車"

        Args:
            guest_token: 訪客識別碼
            user_id: 會員 UUID

        Returns:
            dict: 預覽資訊
            {
                "guest_items_count": 3,
                "guest_total_quantity": 5,
                "has_items": True
            }
        """
        try:
            guest_items = await self.redis_repo.get_cart(guest_token)

            return {
                "guest_items_count": len(guest_items),
                "guest_total_quantity": sum(item.quantity for item in guest_items),
                "has_items": len(guest_items) > 0,
            }
        except Exception:
            return {
                "guest_items_count": 0,
                "guest_total_quantity": 0,
                "has_items": False,
            }
