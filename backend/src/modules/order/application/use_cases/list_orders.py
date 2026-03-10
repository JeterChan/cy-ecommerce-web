"""
Order Module - Use Case: List Orders

列出使用者訂單用例。
"""

from typing import List
from modules.order.domain.entities import Order
from modules.order.domain.repository import IOrderRepository


class ListUserOrdersUseCase:
    """列出使用者訂單用例"""

    def __init__(self, order_repository: IOrderRepository):
        """
        初始化用例

        Args:
            order_repository: 訂單 Repository
        """
        self.order_repo = order_repository

    async def execute(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Order]:
        """
        查詢使用者的所有訂單

        Args:
            user_id: 使用者 ID
            skip: 略過筆數（用於分頁）
            limit: 限制筆數（用於分頁，預設 20）

        Returns:
            List[Order]: 訂單列表（依建立時間降序排列）
        """
        # 驗證分頁參數
        if skip < 0:
            skip = 0

        if limit < 1:
            limit = 20
        elif limit > 100:
            limit = 100  # 最多一次查詢 100 筆

        # 查詢訂單列表
        orders = await self.order_repo.get_by_user_id(
            user_id=user_id,
            skip=skip,
            limit=limit
        )

        return orders


