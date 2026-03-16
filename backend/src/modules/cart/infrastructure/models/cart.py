from shared.infrastructure.orm import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, CheckConstraint, Index, ForeignKey, UUID, String
from typing import List, Optional
import uuid


class CartModel(BaseModel):
    """
    購物車 SQLAlchemy Model

    設計考量:
    1. 支援雙重識別：會員 (user_id) 或訪客 (guest_token)
    2. 會員購物車持久化在 DB，訪客購物車在 Redis（但合併時會暫存）
    3. 購物車與 CartItem 是 1:N 關係
    """
    __tablename__ = "carts"

    # === 擁有者識別 (二選一) ===
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="會員 ID (會員購物車使用)"
    )

    guest_token: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="訪客識別碼 (訪客購物車暫存使用)"
    )

    # === 關聯 ===
    items: Mapped[List["CartItemModel"]] = relationship(
        "CartItemModel",
        back_populates="cart",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # === 約束條件 ===
    __table_args__ = (
        # 1. 必須有 user_id 或 guest_token 其中之一（但不能同時有）
        CheckConstraint(
            '(user_id IS NOT NULL AND guest_token IS NULL) OR (user_id IS NULL AND guest_token IS NOT NULL)',
            name='ck_carts_owner_exclusivity'
        ),

        # 2. 每個會員只能有一個購物車
        Index(
            'ix_carts_user_unique',
            'user_id',
            unique=True,
            postgresql_where='user_id IS NOT NULL'
        ),

        # 3. 每個訪客 token 只能有一個購物車
        Index(
            'ix_carts_guest_unique',
            'guest_token',
            unique=True,
            postgresql_where='guest_token IS NOT NULL'
        ),
    )


class CartItemModel(BaseModel):
    """
    購物車項目 SQLAlchemy Model

    設計考量:
    1. 屬於某個購物車 (cart_id)
    2. 透過 cart 關聯取得 user_id 或 guest_token
    3. 不儲存價格快照（購物車階段動態查詢 Product 價格）
    4. 價格快照只在結帳時儲存到 OrderItem
    5. 數量必須 > 0
    """
    __tablename__ = "cart_items"

    # === 購物車關聯 ===
    cart_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="購物車 ID"
    )

    # === 商品資訊 ===
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        # ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="商品 UUID"
    )

    # === 數量 ===
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="購買數量 (必須 > 0)"
    )

    # === 關聯 ===
    cart: Mapped["CartModel"] = relationship(
        "CartModel",
        back_populates="items"
    )

    # === 約束條件 ===
    __table_args__ = (
        # 1. 數量必須大於 0
        CheckConstraint('quantity > 0', name='ck_cart_items_quantity_positive'),

        # 2. 同一購物車不能有重複的商品
        Index(
            'ix_cart_items_cart_product_unique',
            'cart_id', 'product_id',
            unique=True
        ),
    )

