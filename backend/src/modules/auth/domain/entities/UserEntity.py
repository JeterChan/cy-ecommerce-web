from shared.domain.entity import BaseEntity
from pydantic import EmailStr
from datetime import datetime, timezone
from typing import Optional

class UserEntity(BaseEntity):
    """User Domain Entity - 包含業務邏輯"""
    email: EmailStr
    username: str
    password_hash: str
    is_active: bool = True

    # 個人檔案欄位 (spec-defined)
    display_name: str | None = None
    phone_number: str | None = None
    avatar_url: str | None = None
    bio: str | None = None

    # 發票/載具欄位
    phone: str | None = None
    address: str | None = None
    carrier_type: str | None = None  # 載具類型：MOBILE, CITIZEN_CARD, DONATE
    carrier_number: str | None = None  # 載具號碼
    tax_id: str | None = None  # 統一編號

    # 帳號刪除欄位（軟刪除）
    deleted_at: Optional[datetime] = None

    def activate(self) -> None:
        """啟用使用者帳號"""
        self.is_active = True

    def deactivate(self) -> None:
        """停用使用者帳號"""
        self.is_active = False

    def soft_delete(self) -> None:
        """軟刪除使用者帳號"""
        self.deleted_at = datetime.now(timezone.utc)
        self.is_active = False

    def is_deleted(self) -> bool:
        """檢查使用者是否已被軟刪除"""
        return self.deleted_at is not None

    def verify_password(self, plain_password: str) -> bool:
        """驗證密碼"""
        from core.security import verify_password
        return verify_password(plain_password, self.password_hash)
