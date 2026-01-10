from pydantic import BaseModel, EmailStr, Field, field_validator, UUID4
from datetime import datetime
from typing import Optional

# Use Case : register
class RegisterUserInputDTO(BaseModel):
    """註冊 Use Case 的 Input"""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="User name",
        examples=["john_doe", "alice_smith"]
    )

    email: EmailStr = Field(
        ...,
        description="電子郵件",
        examples=["user@example.com"]
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="密碼",
        examples=["SecurePassword123!"]
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        """
        Validate and normalize a username.
        
        Enforces that the username contains only letters, digits, underscores, or hyphens and does not start or end with an underscore or hyphen; returns the username converted to lowercase.
        
        Parameters:
            value (str): The raw username to validate.
        
        Returns:
            str: The validated username in lowercase.
        
        Raises:
            ValueError: If the username contains invalid characters or starts/ends with an underscore or hyphen.
        """
        if not value.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )

        if value.startswith(("_", "-")) or value.endswith(("_", "-")):
            raise ValueError(
                "Username cannot start or end with underscore or hyphen"
            )

        return value.lower()  # 統一轉為小寫

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """
        Ensure the password contains at least one uppercase letter, one lowercase letter, and one digit.
        
        Returns:
            The original password string.
        
        Raises:
            ValueError: If the password is missing an uppercase letter, lowercase letter, or digit.
        """
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter")

        if not any(c.islower() for c in value):
            raise ValueError("Password must contain at least one lowercase letter")

        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit")

        return value

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "SecurePass123!"
            }
        }

class RegisterUserOutputDTO(BaseModel):
    """
    註冊 Use Case 的 Output DTO
    職責：
    - 定義 Use Case 返回的資料結構
    - 隱藏敏感資訊（如 hashed_password）
    - 提供給 API Layer 使用
    """

    id: UUID4 = Field(..., description="使用者 ID")
    username: str = Field(..., description="使用者名稱")
    email: EmailStr = Field(..., description="電子郵件")
    is_active: bool = Field(..., description="是否啟用")
    created_at: Optional[datetime] = Field(None, description="建立時間")

    class Config:
        from_attributes = True  # 允許從 ORM 模型轉換
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }