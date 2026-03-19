"""
Order Module - PostgreSQL Repository Implementation

此檔案實作訂單的 PostgreSQL Repository。
"""

from datetime import date, datetime, time
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Date
from modules.order.domain.repository import IOrderRepository
from modules.order.domain.entities import Order, OrderItem
from modules.order.domain.value_objects import OrderStatus
from modules.order.infrastructure.models import OrderModel, OrderItemModel
from decimal import Decimal


class PostgresOrderRepository(IOrderRepository):
    """訂單的 PostgreSQL Repository 實作"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, order: Order) -> Order:
        # 將 Domain Entity 轉換為 ORM Model
        order_model = OrderModel(
            user_id=order.user_id,
            order_number=order.order_number,
            status=OrderStatus(order.status) if isinstance(order.status, str) else order.status,
            total_amount=float(order.total_amount),
            shipping_fee=float(order.shipping_fee),
            note=order.note,
            admin_note=order.admin_note,
            recipient_name=order.recipient_name,
            recipient_phone=order.recipient_phone,
            shipping_address=order.shipping_address,
            payment_method=order.payment_method,
            status_updated_at=func.now() # Initial status timestamp
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

    async def get_by_id(self, order_id: UUID) -> Optional[Order]:
        stmt = select(OrderModel).where(OrderModel.id == order_id)
        result = await self.session.execute(stmt)
        order_model = result.unique().scalar_one_or_none()

        if order_model is None:
            return None

        return self._to_domain_entity(order_model)

    async def get_by_user_id(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        stmt = (
            select(OrderModel)
            .where(OrderModel.user_id == user_id)
            .order_by(OrderModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        order_models = result.unique().scalars().all()

        return [self._to_domain_entity(om) for om in order_models]

    async def count_by_user_id(self, user_id: UUID) -> int:
        stmt = select(func.count()).select_from(OrderModel).where(OrderModel.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        search_order_number: Optional[str] = None,
        search_recipient_name: Optional[str] = None,
        search_phone: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> List[Order]:
        stmt = select(OrderModel).order_by(OrderModel.created_at.desc())
        stmt = self._apply_filters(stmt, status, search_order_number, search_recipient_name, search_phone, date_from, date_to)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        order_models = result.unique().scalars().all()
        return [self._to_domain_entity(om) for om in order_models]

    async def count_all(
        self,
        status: Optional[str] = None,
        search_order_number: Optional[str] = None,
        search_recipient_name: Optional[str] = None,
        search_phone: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> int:
        stmt = select(func.count()).select_from(OrderModel)
        stmt = self._apply_filters(stmt, status, search_order_number, search_recipient_name, search_phone, date_from, date_to)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    def _apply_filters(self, stmt, status, search_order_number, search_recipient_name, search_phone, date_from, date_to):
        if status:
            stmt = stmt.where(OrderModel.status == OrderStatus(status.upper()))
        if search_order_number:
            stmt = stmt.where(OrderModel.order_number.ilike(f"%{search_order_number}%"))
        if search_recipient_name:
            stmt = stmt.where(OrderModel.recipient_name.ilike(f"%{search_recipient_name}%"))
        if search_phone:
            stmt = stmt.where(OrderModel.recipient_phone.ilike(f"%{search_phone}%"))
        if date_from:
            stmt = stmt.where(OrderModel.created_at >= datetime.combine(date_from, time.min))
        if date_to:
            stmt = stmt.where(OrderModel.created_at <= datetime.combine(date_to, time.max))
        return stmt

    async def update(self, order: Order) -> Order:
        stmt = select(OrderModel).where(OrderModel.id == order.id)
        result = await self.session.execute(stmt)
        order_model = result.unique().scalar_one_or_none()

        if order_model is None:
            raise ValueError(f"訂單 {order.id} 不存在")

        # 檢查狀態是否改變
        new_status = OrderStatus(order.status) if isinstance(order.status, str) else order.status
        if order_model.status != new_status:
            order_model.status_updated_at = func.now()

        # 更新欄位
        order_model.status = new_status
        order_model.total_amount = float(order.total_amount)
        order_model.shipping_fee = float(order.shipping_fee)
        order_model.note = order.note
        order_model.admin_note = order.admin_note
        order_model.recipient_name = order.recipient_name
        order_model.recipient_phone = order.recipient_phone
        order_model.shipping_address = order.shipping_address
        order_model.payment_method = order.payment_method

        await self.session.flush()
        await self.session.refresh(order_model)

        return self._to_domain_entity(order_model)

    async def get_today_stats(self) -> dict:
        """取得台灣時區今日訂單數及銷售額（排除 CANCELLED、REFUNDED）"""
        taipei_date = cast(func.timezone('Asia/Taipei', OrderModel.created_at), Date)
        today_taipei = cast(func.timezone('Asia/Taipei', func.now()), Date)
        excluded_statuses = [OrderStatus.CANCELLED, OrderStatus.REFUNDED]

        stmt = (
            select(
                func.count().label('count'),
                func.coalesce(func.sum(OrderModel.total_amount), 0).label('total_sales')
            )
            .select_from(OrderModel)
            .where(taipei_date == today_taipei)
            .where(OrderModel.status.notin_(excluded_statuses))
        )
        result = await self.session.execute(stmt)
        row = result.one()
        return {'count': row.count, 'total_sales': Decimal(str(row.total_sales))}

    async def delete(self, order_id: UUID) -> bool:
        stmt = select(OrderModel).where(OrderModel.id == order_id)
        result = await self.session.execute(stmt)
        order_model = result.unique().scalar_one_or_none()

        if order_model is None:
            return False

        await self.session.delete(order_model)
        await self.session.flush()

        return True

    def _to_domain_entity(self, order_model: OrderModel) -> Order:
        items = [
            OrderItem(
                id=item.id,
                order_id=item.order_id,
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=Decimal(str(item.unit_price)),
                subtotal=Decimal(str(item.subtotal)),
                created_at=None,
                updated_at=None
            )
            for item in order_model.items
        ]
        
        return Order(
            id=order_model.id,
            user_id=order_model.user_id,
            order_number=order_model.order_number,
            status=order_model.status.value,
            total_amount=Decimal(str(order_model.total_amount)),
            shipping_fee=Decimal(str(order_model.shipping_fee)),
            note=order_model.note,
            admin_note=order_model.admin_note,
            recipient_name=order_model.recipient_name,
            recipient_phone=order_model.recipient_phone,
            shipping_address=order_model.shipping_address,
            payment_method=order_model.payment_method,
            items=items,
            created_at=order_model.created_at,
            updated_at=order_model.updated_at,
            status_updated_at=order_model.status_updated_at
        )

