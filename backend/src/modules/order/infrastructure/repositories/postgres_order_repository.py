"""
Order Module - PostgreSQL Repository Implementation

此檔案實作訂單的 PostgreSQL Repository。
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from modules.order.domain.repository import IOrderRepository
from modules.order.domain.entities import Order, OrderItem
from modules.order.domain.value_objects import OrderStatus
from modules.order.infrastructure.models import OrderModel, OrderItemModel
from decimal import Decimal


class PostgresOrderRepository(IOrderRepository):
    """訂單的 PostgreSQL Repository 實作"""

    def __init__(self, session: AsyncSession):
        """
        初始化 Repository

        Args:
            session: SQLAlchemy AsyncSession
        """
        self.session = session

    async def create(self, order: Order) -> Order:
        """
        建立新訂單

        Args:
            order: 訂單實體

        Returns:
            Order: 建立完成的訂單（包含生成的 ID）
        """
        # 將 Domain Entity 轉換為 ORM Model
        order_model = OrderModel(
            user_id=order.user_id,
            status=OrderStatus(order.status) if isinstance(order.status, str) else order.status,
            total_amount=float(order.total_amount),
            shipping_fee=float(order.shipping_fee),
            note=order.note
        )

        # 轉換訂單項目
        for item in order.items:
            item_model = OrderItemModel(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=float(item.unit_price),
                subtotal=float(item.subtotal)
            )
            order_model.items.append(item_model)

        # 儲存至資料庫
        self.session.add(order_model)
        await self.session.flush()  # 取得 ID
        await self.session.refresh(order_model)

        # 將 ORM Model 轉換回 Domain Entity
        return self._to_domain_entity(order_model)

    async def get_by_id(self, order_id: int) -> Optional[Order]:
        """
        根據 ID 查詢訂單

        Args:
            order_id: 訂單 ID

        Returns:
            Optional[Order]: 訂單實體，若不存在則回傳 None
        """
        stmt = select(OrderModel).where(OrderModel.id == order_id)
        result = await self.session.execute(stmt)
        # 使用 unique() 過濾因為 joined eager loading 產生的重複結果
        order_model = result.unique().scalar_one_or_none()

        if order_model is None:
            return None

        return self._to_domain_entity(order_model)

    async def get_by_user_id(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """
        查詢特定使用者的所有訂單

        Args:
            user_id: 使用者 ID
            skip: 略過筆數（用於分頁）
            limit: 限制筆數（用於分頁）

        Returns:
            List[Order]: 訂單列表
        """
        stmt = (
            select(OrderModel)
            .where(OrderModel.user_id == user_id)
            .order_by(OrderModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        # 使用 unique() 過濾因為 joined eager loading 產生的重複結果
        order_models = result.unique().scalars().all()

        return [self._to_domain_entity(om) for om in order_models]

    async def update(self, order: Order) -> Order:
        """
        更新訂單

        Args:
            order: 訂單實體

        Returns:
            Order: 更新後的訂單
        """
        stmt = select(OrderModel).where(OrderModel.id == order.id)
        result = await self.session.execute(stmt)
        # 使用 unique() 過濾因為 joined eager loading 產生的重複結果
        order_model = result.unique().scalar_one_or_none()

        if order_model is None:
            raise ValueError(f"訂單 {order.id} 不存在")

        # 更新欄位
        order_model.status = OrderStatus(order.status) if isinstance(order.status, str) else order.status
        order_model.total_amount = float(order.total_amount)
        order_model.shipping_fee = float(order.shipping_fee)
        order_model.note = order.note

        await self.session.flush()
        await self.session.refresh(order_model)

        return self._to_domain_entity(order_model)

    async def delete(self, order_id: int) -> bool:
        """
        刪除訂單

        Args:
            order_id: 訂單 ID

        Returns:
            bool: 是否成功刪除
        """
        stmt = select(OrderModel).where(OrderModel.id == order_id)
        result = await self.session.execute(stmt)
        # 使用 unique() 過濾因為 joined eager loading 產生的重複結果
        order_model = result.unique().scalar_one_or_none()

        if order_model is None:
            return False

        await self.session.delete(order_model)
        await self.session.flush()

        return True

    def _to_domain_entity(self, order_model: OrderModel) -> Order:
        """
        將 ORM Model 轉換為 Domain Entity

        Args:
            order_model: OrderModel 實例

        Returns:
            Order: 訂單領域實體
        """
        items = [
            OrderItem(
                id=item.id,
                order_id=item.order_id,
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=Decimal(str(item.unit_price)),
                subtotal=Decimal(str(item.subtotal)),
                created_at=item.created_at,
                updated_at=item.updated_at
            )
            for item in order_model.items
        ]

        return Order(
            id=order_model.id,
            user_id=order_model.user_id,
            status=order_model.status.value,
            total_amount=Decimal(str(order_model.total_amount)),
            shipping_fee=Decimal(str(order_model.shipping_fee)),
            note=order_model.note,
            items=items,
            created_at=order_model.created_at,
            updated_at=order_model.updated_at
        )

