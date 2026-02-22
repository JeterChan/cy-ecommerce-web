"""
Order Module - Use Case: Update Order

更新訂單用例。
"""

from modules.order.domain.entities import Order
from modules.order.domain.value_objects import OrderStatus
from modules.order.domain.repository import IOrderRepository
from shared.exceptions import ResourceNotFoundException, BusinessRuleViolationException


class UpdateOrderStatusUseCase:
    """更新訂單狀態用例"""

    def __init__(self, order_repository: IOrderRepository):
        """
        初始化用例

        Args:
            order_repository: 訂單 Repository
        """
        self.order_repo = order_repository

    async def execute(
        self,
        order_id: int,
        new_status: str,
        user_id: str | None = None
    ) -> Order:
        """
        更新訂單狀態

        Args:
            order_id: 訂單 ID
            new_status: 新的訂單狀態
            user_id: 使用者 ID（用於權限驗證，管理員可傳 None）

        Returns:
            Order: 更新後的訂單實體

        Raises:
            ResourceNotFoundException: 訂單不存在
            PermissionError: 無權限修改此訂單
            BusinessRuleViolationException: 狀態轉換不合法
        """
        # 1. 查詢訂單
        order = await self.order_repo.get_by_id(order_id)

        if order is None:
            raise ResourceNotFoundException(f"訂單 {order_id} 不存在")

        # 2. 驗證使用者權限（如果提供 user_id）
        if user_id is not None and order.user_id != user_id:
            raise PermissionError(f"無權限修改訂單 {order_id}")

        # 3. 驗證新狀態是否有效
        try:
            new_order_status = OrderStatus(new_status)
        except ValueError:
            raise BusinessRuleViolationException(
                f"無效的訂單狀態: {new_status}。有效值: {', '.join([s.value for s in OrderStatus])}"
            )

        # 4. 驗證狀態轉換是否合法
        self._validate_status_transition(order.status, new_order_status.value)

        # 5. 更新訂單狀態
        order.status = new_order_status.value

        # 6. 儲存更新
        updated_order = await self.order_repo.update(order)

        return updated_order

    def _validate_status_transition(self, current_status: str, new_status: str) -> None:
        """
        驗證訂單狀態轉換是否合法

        業務規則：
        - PENDING 可以轉換到 PAID, CANCELLED
        - PAID 可以轉換到 SHIPPED, REFUNDED, CANCELLED
        - SHIPPED 可以轉換到 COMPLETED, REFUNDED
        - COMPLETED 可以轉換到 REFUNDED
        - CANCELLED 和 REFUNDED 是終態，不可再轉換

        Args:
            current_status: 當前狀態
            new_status: 新狀態

        Raises:
            BusinessRuleViolationException: 狀態轉換不合法
        """
        # 如果狀態相同，允許（冪等性）
        if current_status == new_status:
            return

        # 定義合法的狀態轉換
        allowed_transitions = {
            OrderStatus.PENDING.value: [
                OrderStatus.PAID.value,
                OrderStatus.CANCELLED.value
            ],
            OrderStatus.PAID.value: [
                OrderStatus.SHIPPED.value,
                OrderStatus.REFUNDED.value,
                OrderStatus.CANCELLED.value
            ],
            OrderStatus.SHIPPED.value: [
                OrderStatus.COMPLETED.value,
                OrderStatus.REFUNDED.value
            ],
            OrderStatus.COMPLETED.value: [
                OrderStatus.REFUNDED.value
            ],
            OrderStatus.CANCELLED.value: [],  # 終態
            OrderStatus.REFUNDED.value: []    # 終態
        }

        # 檢查轉換是否合法
        if new_status not in allowed_transitions.get(current_status, []):
            raise BusinessRuleViolationException(
                f"不允許從 {current_status} 轉換到 {new_status}。"
                f"允許的狀態: {', '.join(allowed_transitions.get(current_status, []))}"
            )


