"""
Auth Input DTOs

用於接收來自 API 的請求資料
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict


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

