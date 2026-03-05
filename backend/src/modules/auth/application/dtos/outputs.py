"""
Auth Output DTOs

用於回傳給 API 的響應資料
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

from modules.auth.domain.entities.UserEntity import UserEntity


class UserResponseDTO(BaseModel):
    """
    使用者資料的 Output DTO

    用於回傳使用者資訊
    """
    id: UUID = Field(..., description="使用者 ID")
    email: EmailStr = Field(..., description="使用者信箱")
    username: str = Field(..., description="使用者名稱")
    is_active: bool = Field(default=True, description="帳號啟用狀態")
    created_at: datetime = Field(..., description="建立時間")
    updated_at: Optional[datetime] = Field(None, description="更新時間")

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: str,
            datetime: lambda v: v.isoformat() if v else None,
        },
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "username": "john_doe",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
    )


class TokenResponseDTO(BaseModel):
    """
    Token 回應的 Output DTO

    用於回傳 JWT Token
    """
    access_token: str = Field(..., description="JWT Access Token")
    token_type: str = Field(default="bearer", description="Token 類型")
    refresh_token: Optional[str] = Field(None, description="JWT Refresh Token (可選)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "refresh_token": None
            }
        }
    )


class LoginResponseDTO(TokenResponseDTO):
    """
    登入回應的 Output DTO

    用於 POST /auth/login 的回應
    繼承 TokenResponseDTO 並加入使用者資料
    """
    user: UserResponseDTO = Field(..., description="使用者資料")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com",
                    "username": "john_doe",
                    "is_active": True,
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z"
                }
            }
        }
    )

class UserProfileResponse(BaseModel):
    """使用者個人檔案回應 DTO"""
    user_id: str = Field(..., description="使用者 ID")
    username: str = Field(..., description="使用者名稱")
    email: str = Field(..., description="電子郵件")
    phone: Optional[str] = Field(None, description="聯絡電話")
    address: Optional[str] = Field(None, description="郵寄地址")
    carrier_type: Optional[str] = Field(None, description="載具類型")
    carrier_number: Optional[str] = Field(None, description="載具號碼")
    tax_id: Optional[str] = Field(None, description="統一編號")
    is_active: bool = Field(True, description="帳號啟用狀態")
    created_at: str = Field(..., description="建立時間 (ISO 8601)")
    updated_at: str = Field(..., description="更新時間 (ISO 8601)")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_entity(cls, user: UserEntity) -> "UserProfileResponse":
        """從 UserEntity 建立 DTO"""
        return cls(
            user_id=str(user.id),
            username=user.username,
            email=str(user.email),
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat() if user.updated_at else user.created_at.isoformat(),
            phone=user.phone,
            address=user.address,
            carrier_type=user.carrier_type,
            carrier_number=user.carrier_number,
            tax_id=user.tax_id,
            is_active=user.is_active,
        )


class UpdateProfileResponse(BaseModel):
    """更新個人檔案回應 DTO"""
    user_id: str = Field(..., description="使用者 ID")
    username: str = Field(..., description="使用者名稱")
    email: str = Field(..., description="電子郵件")
    phone: Optional[str] = Field(None, description="聯絡電話")
    address: Optional[str] = Field(None, description="郵寄地址")
    carrier_type: Optional[str] = Field(None, description="載具類型")
    carrier_number: Optional[str] = Field(None, description="載具號碼")
    tax_id: Optional[str] = Field(None, description="統一編號")
    is_active: bool = Field(True, description="帳號啟用狀態")
    created_at: str = Field(..., description="建立時間 (ISO 8601)")
    updated_at: str = Field(..., description="更新時間 (ISO 8601)")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_entity(cls, user: UserEntity) -> "UpdateProfileResponse":
        """從 UserEntity 建立 DTO"""
        return cls(
            user_id=str(user.id),
            username=user.username,
            email=str(user.email),
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat() if user.updated_at else user.created_at.isoformat(),
            phone=user.phone,
            address=user.address,
            carrier_type=user.carrier_type,
            carrier_number=user.carrier_number,
            tax_id=user.tax_id,
            is_active=user.is_active,
        )