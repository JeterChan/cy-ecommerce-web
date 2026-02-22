"""
Order Module - Use Case: Get Order

查詢訂單用例。
"""

from modules.order.domain.entities import Order
from modules.order.domain.repository import IOrderRepository
from shared.exceptions import ResourceNotFoundException


class GetOrderUseCase:
    """查詢訂單用例"""

    def __init__(self, order_repository: IOrderRepository):
        """
        初始化用例

        Args:
            order_repository: 訂單 Repository
        """
        self.order_repo = order_repository

    async def execute(self, order_id: int, user_id: str) -> Order:
        """
        查詢訂單詳情

        Args:
            order_id: 訂單 ID
            user_id: 使用者 ID（用於權限驗證）

        Returns:
            Order: 訂單實體

        Raises:
            ResourceNotFoundException: 訂單不存在
            PermissionError: 無權限查看此訂單
        """
        # 查詢訂單
        order = await self.order_repo.get_by_id(order_id)

        if order is None:
            raise ResourceNotFoundException(f"訂單 {order_id} 不存在")

        # 驗證使用者權限（只能查看自己的訂單）
        if order.user_id != user_id:
            raise PermissionError(f"無權限查看訂單 {order_id}")

        return order


