from pydantic import BaseModel, EmailStr, Field, ConfigDict, UUID4
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
    id: UUID4 = Field(..., description="使用者ID")
    is_activate: bool = Field(default=True, description="帳號啟用狀態")
    created_at: datetime = Field(..., description="建立時間")
    updated_at: datetime = Field(..., description="更新時間")

    model_config = ConfigDict(
        from_attributes=True, # 允許從 User Entity 讀取
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

