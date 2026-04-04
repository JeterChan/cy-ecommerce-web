from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from modules.order.domain.repository import IOrderRepository
from modules.order.domain.value_objects import OrderStatus
from modules.order.domain.ports import IProductPort

class AdminUpdateOrderUseCase:
    def __init__(
        self,
        db: AsyncSession,
        order_repo: IOrderRepository,
        product_port: IProductPort
    ):
        self.db = db
        self.order_repo = order_repo
        self.product_port = product_port

    async def execute(
        self,
        order_id: UUID,
        new_status: Optional[str] = None,
        admin_note: Optional[str] = None
    ):
        """
        管理員更新訂單。支援更新狀態與內部備註。
        """
        # 如果已經在交易中，直接執行內容；否則開啟新交易
        if self.db.in_transaction():
            return await self._do_execute(order_id, new_status, admin_note)

        async with self.db.begin():
            return await self._do_execute(order_id, new_status, admin_note)

    async def _do_execute(self, order_id: UUID, new_status: Optional[str], admin_note: Optional[str]):
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("訂單不存在")

        if admin_note is not None:
            order.admin_note = admin_note

        if new_status:
            old_status = order.status
            try:
                target_status = OrderStatus(new_status.upper())
            except ValueError:
                raise ValueError(f"無效的訂單狀態: {new_status}")

            if old_status != target_status.value:
                # 如果是取消訂單，且原本是 PENDING 或 PAID，則回補庫存
                if target_status == OrderStatus.CANCELLED and old_status in [OrderStatus.PENDING.value, OrderStatus.PAID.value]:
                    for item in order.items:
                        await self.product_port.restore_stock(item.product_id, item.quantity)

                # 基本的狀態跳轉檢查
                if old_status == OrderStatus.CANCELLED.value and target_status != OrderStatus.CANCELLED:
                     raise ValueError("已取消的訂單不可恢復狀態")

                order.status = target_status.value

        updated_order = await self.order_repo.update(order)
        return updated_order
