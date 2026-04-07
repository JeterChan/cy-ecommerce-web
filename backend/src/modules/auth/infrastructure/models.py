from shared.infrastructure.orm import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, Text, DateTime
from datetime import datetime
from typing import Optional


class UserModel(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user", server_default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # 個人檔案欄位
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    carrier_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # 載具類型
    carrier_number: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # 載具號碼
    tax_id: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 統一編號

    # 帳號刪除欄位（軟刪除）
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
