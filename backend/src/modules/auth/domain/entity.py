from shared.domain.entity import BaseEntity
from pydantic import EmailStr

class UserEntity(BaseEntity):
    """User Domain Entity - 包含業務邏輯"""
    email:EmailStr
    username:str
    password_hash:str
    is_active: bool = True

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
