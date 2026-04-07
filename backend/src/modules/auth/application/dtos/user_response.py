from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserResponseDTO(BaseModel):
    """使用者資料的回應 DTO"""

    id: UUID = Field(..., description="使用者 ID")
    email: EmailStr = Field(..., description="使用者信箱")
    username: str = Field(..., description="使用者名稱")
    role: str = Field(default="user", description="使用者角色")
    is_active: bool = Field(default=True, description="帳號啟用狀態")
    created_at: datetime = Field(..., description="建立時間")
    updated_at: Optional[datetime] = Field(None, description="更新時間")

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: str,
            datetime: lambda v: v.isoformat() if v else None,
        },
    )
