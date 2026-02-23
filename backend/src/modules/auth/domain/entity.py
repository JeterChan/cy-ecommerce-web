from shared.domain.entity import BaseEntity
from pydantic import EmailStr

class UserEntity(BaseEntity):
    """User Domain Entity - 包含業務邏輯"""
    email: EmailStr
    username: str
    password_hash: str
    is_active: bool = True

    # 個人檔案欄位
    phone: str | None = None
    address: str | None = None
    carrier_type: str | None = None  # 載具類型：MOBILE, CITIZEN_CARD, DONATE
    carrier_number: str | None = None  # 載具號碼
    tax_id: str | None = None  # 統一編號

    def activate(self) -> None:
        """啟用使用者帳號"""
        self.is_active = True

    def deactivate(self) -> None:
        """停用使用者帳號"""
        self.is_active = False

    def verify_password(self, plain_password: str) -> bool:
        """驗證密碼"""
        from core.security import verify_password
        return verify_password(plain_password, self.password_hash)
