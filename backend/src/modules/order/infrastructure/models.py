"""
Order Module - SQLAlchemy Models

此檔案定義訂單相關的 ORM 模型。
"""

from sqlalchemy import Integer, String, Numeric, Enum as SQLEnum, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from datetime import datetime
from uuid import UUID
from infrastructure.database import Base
from modules.order.domain.value_objects import OrderStatus


class OrderModel(Base):
    """訂單主檔資料表"""
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 使用者 ID（關聯 User，此處使用 String 因為可能是 UUID 或 guest token）
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # 訂單狀態
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus, native_enum=False),
        nullable=False,
        default=OrderStatus.PENDING,
        index=True
    )

    # 訂單金額
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    shipping_fee: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    # 訂單備註
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # 時間戳記
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # 關聯訂單項目（一對多）
    items: Mapped[list["OrderItemModel"]] = relationship(
        "OrderItemModel",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="joined"  # 查詢訂單時自動載入項目
    )

    def __repr__(self) -> str:
        return f"<OrderModel(id={self.id}, user_id={self.user_id}, status={self.status}, total={self.total_amount})>"


class OrderItemModel(Base):
    """訂單項目資料表"""
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 關聯訂單 ID（外鍵）
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # 商品 ID（UUID 格式，不使用外鍵，因為商品可能被刪除但訂單要保留）
    product_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)

    # 商品名稱快照（避免商品被刪除或改名後無法顯示）
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # 購買數量
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # 價格快照（購買時的單價，不隨商品價格變動）
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # 小計（quantity * unit_price）
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # 時間戳記
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # 反向關聯訂單
    order: Mapped["OrderModel"] = relationship("OrderModel", back_populates="items")

    def __repr__(self) -> str:
        return f"<OrderItemModel(id={self.id}, order_id={self.order_id}, product={self.product_name}, qty={self.quantity})>"


