from sqlalchemy import (
    Integer,
    String,
    Numeric,
    Boolean,
    ForeignKey,
    DateTime,
    Column,
    func,
    UUID,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from infrastructure.database import Base
import uuid

# association_table removed


class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="商品 UUID"
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # ✅ 使用 SQLAlchemy 的 func.now() 在資料庫層面處理時間戳
    # 避免 Python datetime.utcnow() 的過時警告
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    category: Mapped["CategoryModel"] = relationship(
        "CategoryModel", back_populates="products", lazy="joined"
    )

    images: Mapped[list["ProductImageModel"]] = relationship(
        "ProductImageModel",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class ProductImageModel(Base):
    __tablename__ = "product_images"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    alt_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    product: Mapped["ProductModel"] = relationship(
        "ProductModel", back_populates="images"
    )


class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    products: Mapped[list["ProductModel"]] = relationship(
        "ProductModel", back_populates="category"
    )
