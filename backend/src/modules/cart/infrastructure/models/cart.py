from shared.infrastructure.orm import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, CheckConstraint, Index, ForeignKey, UUID
from typing import Optional
import uuid


class CartItemModel(BaseModel):
    """
    購物車項目 SQLAlchemy Model (僅限會員購物車)

    設計考量:
    1. 訪客購物車使用 Redis 儲存，不需要 DB model
    2. 會員購物車需要持久化，儲存於 PostgreSQL
    3. 支援雙重識別：user_id (會員) 或 guest_token (訪客登入前的遺留資料)
    4. 與 Product 表的關聯採用 product_id (UUID)
    5. 包含數量驗證 (必須 > 0)
    """
    __tablename__ = "cart_items"

    # === 擁有者識別 (二選一) ===
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),  # 使用者刪除時級聯刪除購物車
        nullable=True,
        index=True,  # 查詢優化：依 user_id 查詢購物車
        comment="會員 ID (會員購物車使用)"
    )

    guest_token: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,  # 查詢優化：依 guest_token 查詢購物車
        comment="訪客識別碼 (訪客購物車暫存使用，通常會在登入後合併至會員購物車)"
    )

    # === 商品資訊 ===
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        # ForeignKey("products.id", ondelete="RESTRICT"),  # 商品刪除時限制
        nullable=False,
        index=True,  # 查詢優化：商品查詢
        comment="商品 UUID (參照 products 表)"
    )

    # === 數量 ===
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="購買數量 (必須 > 0)"
    )

    # === 約束條件 ===
    __table_args__ = (
        # 1. 數量必須大於 0
        CheckConstraint('quantity > 0', name='ck_cart_items_quantity_positive'),

        # 2. 確保同一擁有者 (user_id 或 guest_token) 不會有重複的商品
        # 會員購物車：user_id + product_id 唯一
        Index(
            'ix_cart_items_user_product_unique',
            'user_id', 'product_id',
            unique=True,
            postgresql_where='user_id IS NOT NULL'
        ),

        # 訪客購物車：guest_token + product_id 唯一
        Index(
            'ix_cart_items_guest_product_unique',
            'guest_token', 'product_id',
            unique=True,
            postgresql_where='guest_token IS NOT NULL'
        ),

        # 3. 確保必須擁有 user_id 或 guest_token 其中之一 (但不能同時有)
        CheckConstraint(
            '(user_id IS NOT NULL AND guest_token IS NULL) OR (user_id IS NULL AND guest_token IS NOT NULL)',
            name='ck_cart_items_owner_exclusivity'
        ),
    )
