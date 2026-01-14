from pydantic import BaseModel, EmailStr, Field, field_validator, UUID4
from datetime import datetime
from typing import Optional
from modules.auth.domain.value_objects.password import Password

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
        驗證使用者名稱格式

        規則：
        - 只能包含字母、數字、底線、連字號
        - 不能以底線或連字號開頭/結尾
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
        try:
            Password(value=value)
            return value
        except ValueError as e:
            raise ValueError(str(e)) from e

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


# Use Case: login
class LoginUserInputDTO(BaseModel):
    """登入 Use Case 的 Input"""
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

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "SecurePass123!"
            }
        }


class LoginUserOutputDTO(BaseModel):
    """
    登入 Use Case 的 Output DTO
    職責：
    - 返回使用者資料和 JWT tokens
    - 隱藏敏感資訊（如 password_hash）
    """

    # 使用者資料
    id: UUID4 = Field(..., description="使用者 ID")
    username: str = Field(..., description="使用者名稱")
    email: EmailStr = Field(..., description="電子郵件")
    is_active: bool = Field(..., description="是否啟用")
    created_at: Optional[datetime] = Field(None, description="建立時間")
    updated_at: Optional[datetime] = Field(None, description="更新時間")

    # JWT tokens
    access_token: str = Field(..., description="Access Token")
    token_type: str = Field(default="bearer", description="Token 類型")
    refresh_token: Optional[str] = Field(None, description="Refresh Token")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "john_doe",
                "email": "john@example.com",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "refresh_token": None
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
    updated_at: Optional[datetime] = Field(None, description="更新時間")

    class Config:
        from_attributes = True  # 允許從 ORM 模型轉換
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }