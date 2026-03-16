from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from modules.order.domain.repository import IOrderRepository
from modules.order.domain.value_objects import OrderStatus
from modules.product.domain.repository import IProductRepository

class UpdateOrderStatusUseCase:
    def __init__(
        self,
        db: AsyncSession,
        order_repo: IOrderRepository,
        product_repo: IProductRepository
    ):
        self.db = db
        self.order_repo = order_repo
        self.product_repo = product_repo

    async def execute(self, order_id: UUID, user_id: UUID, new_status: str):
        """
        更新訂單狀態。如果是取消訂單，則回補庫存。
        """
        async with self.db.begin():
            order = await self.order_repo.get_by_id(order_id)
            if not order:
                raise ValueError("訂單不存在")
            
            if order.user_id != user_id:
                raise ValueError("無權操作此訂單")

            old_status = order.status
            
            # 轉換為 Enum (如果是字串)
            if isinstance(new_status, str):
                try:
                    target_status = OrderStatus(new_status.upper())
                except ValueError:
                    raise ValueError(f"無效的訂單狀態: {new_status}")
            else:
                target_status = new_status

            if old_status == target_status.value:
                return order

            # 如果是從 PENDING 取消，則回補庫存
            if target_status == OrderStatus.CANCELLED and old_status == OrderStatus.PENDING.value:
                for item in order.items:
                    # 使用 repository 的原子調整方法
                    await self.product_repo.atomic_adjust_stock(item.product_id, item.quantity)

            # 更新狀態
            order.status = target_status.value
            updated_order = await self.order_repo.update(order)
            
            return updated_order
