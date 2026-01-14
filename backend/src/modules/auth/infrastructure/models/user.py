from shared.infrastructure.orm import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean


class UserModel(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True
    )
    username: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
