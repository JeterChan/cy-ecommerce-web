from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from modules.auth.domain.entities.UserEntity import UserEntity

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
