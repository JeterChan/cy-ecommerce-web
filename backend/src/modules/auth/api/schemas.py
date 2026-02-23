from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID
from datetime import datetime

# Base Model
class UserBase(BaseModel):
    """ User 基礎資料 """
    email: EmailStr = Field(..., description="使用者信箱")
    username: str = Field(..., min_length=3, max_length=50, description="使用者名稱")

# Request Schemas (API 輸入)
class RegisterRequest(UserBase):
    """註冊請求"""
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="密碼 (8-100 字元)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "username": "john_doe",
                "password": "SecureP@ssw0rd"
            }
        }
    )


class RegisterResponse(UserBase):
    """使用者資料回應"""
    id: UUID = Field(..., description="使用者ID")
    is_active: bool = Field(default=True, description="帳號啟用狀態")
    created_at: datetime = Field(..., description="建立時間")
    updated_at: Optional[datetime] = Field(None, description="更新時間")

    model_config = ConfigDict(
        from_attributes=True, # 允許從 User Entity 讀取
        json_encoders={
            UUID: str,
            datetime: lambda v: v.isoformat() if v else None,
        },
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "username": "john_doe",
                "is_activate": True,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
    )


# Login Schemas
class LoginRequest(BaseModel):
    """登入請求"""
    email: EmailStr = Field(..., description="使用者信箱")
    password: str = Field(..., min_length=8, description="密碼")
    remember_me: bool = Field(False, description="remember me or not")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecureP@ssw0rd",
                "remember_me": "true"
            }
        }
    )


class TokenResponse(BaseModel):
    """Token 回應"""
    access_token: str = Field(..., description="JWT Access Token")
    token_type: str = Field(default="bearer", description="Token 類型")
    refresh_token: str | None = Field(None, description="JWT Refresh Token (可選)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "refresh_token": None
            }
        }
    )


class LoginResponse(TokenResponse):
    """登入回應 (繼承 TokenResponse)"""
    user: RegisterResponse = Field(..., description="使用者資料")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "refresh_token": None,
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com",
                    "username": "john_doe",
                    "is_activate": True,
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z"
                }
            }
        }
    )


# Refresh Token Schemas
class RefreshTokenRequest(BaseModel):
    """刷新 Token 請求"""
    refresh_token: str = Field(..., description="Refresh Token")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


# Profile Update Schemas
class ProfileUpdateRequest(BaseModel):
    """個人檔案更新請求"""
    phone: Optional[str] = Field(None, max_length=20, description="聯絡電話")
    address: Optional[str] = Field(None, max_length=500, description="郵寄地址")
    carrier_type: Optional[str] = Field(None, max_length=50, description="載具類型")
    carrier_number: Optional[str] = Field(None, max_length=100, description="載具號碼")
    tax_id: Optional[str] = Field(None, max_length=20, description="統一編號")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "phone": "0912345678",
                "address": "台北市信義區信義路五段7號",
                "carrier_type": "MOBILE",
                "carrier_number": "/ABC1234",
                "tax_id": "12345678"
            }
        }
    )


class UserProfileResponse(RegisterResponse):
    """使用者完整檔案回應（包含個人資訊）"""
    phone: Optional[str] = Field(None, description="聯絡電話")
    address: Optional[str] = Field(None, description="郵寄地址")
    carrier_type: Optional[str] = Field(None, description="載具類型")
    carrier_number: Optional[str] = Field(None, description="載具號碼")
    tax_id: Optional[str] = Field(None, description="統一編號")

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
                "updated_at": "2024-01-15T10:30:00Z",
                "phone": "0912345678",
                "address": "台北市信義區信義路五段7號",
                "carrier_type": "MOBILE",
                "carrier_number": "/ABC1234",
                "tax_id": "12345678"
            }
        }
    )

