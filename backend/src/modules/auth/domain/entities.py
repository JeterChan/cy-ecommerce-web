from src.shared.domain.entity import BaseEntity
from pydantic import EmailStr

class UserEntity(BaseEntity):
    """User Domain Entity - 包含業務邏輯"""
    email:EmailStr
    username:str
    password_hash:str
    is_activate: bool = True

    def activate(self) -> None:
        """
        Enable the user account.
        """
        self.is_activate = True

    def deactivate(self) -> None:
        """
        Disable the user account.
        
        Sets the `is_activate` flag to False.
        """
        self.is_activate = False

    def verify_password(self, plain_password: str) -> bool:
        """
        Verify whether a provided plaintext password matches the user's stored password hash.
        
        Parameters:
            plain_password (str): The plaintext password to verify.
        
        Returns:
            bool: True if the password matches the stored hash, False otherwise.
        """
        from src.core.security import verify_password
        return verify_password(plain_password, self.password_hash)