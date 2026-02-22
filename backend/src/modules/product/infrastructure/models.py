from sqlalchemy import Integer, String, Numeric, Boolean, Table, ForeignKey, DateTime, Column, func, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from infrastructure.database import Base
import uuid

association_table = Table(
    'product_categories',
    Base.metadata,
    Column('product_id', UUID(as_uuid=True), ForeignKey('products.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="商品 UUID"
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ✅ 使用 SQLAlchemy 的 func.now() 在資料庫層面處理時間戳
    # 避免 Python datetime.utcnow() 的過時警告
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

    categories: Mapped[list["CategoryModel"]] = relationship(
        "CategoryModel",
        secondary=association_table,
        back_populates="products"
    )

class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    products: Mapped[list["ProductModel"]] = relationship(
        "ProductModel",
        secondary=association_table,
        back_populates="categories"
    )
