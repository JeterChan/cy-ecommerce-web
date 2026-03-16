from sqlalchemy import Integer, String, Numeric, ForeignKey, DateTime, func, UUID, Enum as SqlEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from infrastructure.database import Base
import uuid
from modules.order.domain.value_objects import OrderStatus

class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="系統內部 UUID"
    )

    order_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="易讀的訂單編號 (日期+數字)"
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="使用者 ID"
    )

    status: Mapped[OrderStatus] = mapped_column(
        SqlEnum(OrderStatus),
        nullable=False,
        default=OrderStatus.PENDING,
        comment="訂單狀態"
    )

    total_amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="訂單總金額"
    )

    shipping_fee: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
        comment="運費"
    )

    recipient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    shipping_address: Mapped[str] = mapped_column(String(1000), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)

    note: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        comment="訂單備註"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        index=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    items: Mapped[list["OrderItemModel"]] = relationship(
        "OrderItemModel",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

class OrderItemModel(Base):
    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )
    
    product_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="商品名稱快照"
    )

    unit_price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="結帳時的產品單價快照"
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="購買數量"
    )
    
    subtotal: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="小計"
    )

    order: Mapped["OrderModel"] = relationship("OrderModel", back_populates="items")
