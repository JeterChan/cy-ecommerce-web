"""
Auth Input DTOs

用於接收來自 API 的請求資料
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class RegisterRequestDTO(BaseModel):
    """
    註冊請求的 Input DTO

    用於 POST /auth/register
    """
    email: EmailStr = Field(..., description="使用者信箱")
    username: str = Field(..., min_length=3, max_length=50, description="使用者名稱")
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


class LoginRequestDTO(BaseModel):
    """
    登入請求的 Input DTO

    用於 POST /auth/login
    """
    email: EmailStr = Field(..., description="使用者信箱")
    password: str = Field(..., min_length=8, description="密碼")
    remember_me: bool = Field(False, description="記住我")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecureP@ssw0rd",
                "remember_me": True
            }
        }
    )


class RefreshTokenRequestDTO(BaseModel):
    """
    刷新 Token 請求的 Input DTO

    用於 POST /auth/refresh
    """
    refresh_token: str = Field(..., description="Refresh Token")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


class UpdateProfileRequest(BaseModel):
    """
    更新個人檔案請求的 Input DTO

    用於 PATCH /api/v1/auth/me/profile
    所有欄位皆為選填，僅更新有提供的欄位。
    """
    phone: Optional[str] = Field(
        None,
        max_length=20,
        description="聯絡電話",
        examples=["0912345678"],
    )
    address: Optional[str] = Field(
        None,
        max_length=500,
        description="郵寄地址",
        examples=["台北市信義區信義路五段7號"],
    )
    carrier_type: Optional[str] = Field(
        None,
        max_length=50,
        description="載具類型 (MOBILE, CITIZEN_CARD, DONATE)",
        examples=["MOBILE"],
    )
    carrier_number: Optional[str] = Field(
        None,
        max_length=100,
        description="載具號碼",
        examples=["/ABC1234"],
    )
    tax_id: Optional[str] = Field(
        None,
        max_length=20,
        description="統一編號 (8碼數字)",
        examples=["12345678"],
    )

    @field_validator("tax_id")
    @classmethod
    def validate_tax_id(cls, v: Optional[str]) -> Optional[str]:
        """統一編號格式驗證：8碼數字"""
        if v is not None and not v.isdigit():
            raise ValueError("統一編號必須為數字")
        if v is not None and len(v) != 8:
            raise ValueError("統一編號必須為 8 碼")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "phone": "0912345678",
                "address": "台北市信義區信義路五段7號",
                "carrier_type": "MOBILE",
                "carrier_number": "/ABC1234",
                "tax_id": "12345678",
            }
        }
    )


class EmailChangeRequest(BaseModel):
    """
    更改電子郵件請求的 Input DTO

    用於 POST /api/v1/auth/me/email/change
    需要提供新 email 及目前密碼以確認帳號所有權。
    """
    new_email: EmailStr = Field(..., description="新的電子郵件地址")
    password: str = Field(..., min_length=8, description="目前密碼（用於確認帳號所有權）")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "new_email": "new_email@example.com",
                "password": "SecureP@ssw0rd",
            }
        }
    )


class EmailVerifyType(str, Enum):
    """電子郵件驗證類型"""
    OLD = "old"
    NEW = "new"


class VerifyEmailChangeRequest(BaseModel):
    """
    驗證電子郵件變更請求的 Input DTO

    用於 GET /api/v1/auth/me/email/verify (Query Params)
    """
    token: str = Field(..., description="驗證 Token")
    type: EmailVerifyType = Field(..., description="驗證類型：old（舊信箱）或 new（新信箱）")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "abc123def456...",
                "type": "new",
            }
        }
    )



