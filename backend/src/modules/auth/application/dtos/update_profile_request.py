from typing import Optional
from pydantic import BaseModel, Field, field_validator


class UpdateProfileRequest(BaseModel):
    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="使用者名稱"
    )
    phone: Optional[str] = Field(None, max_length=20, description="聯絡電話")
    address: Optional[str] = Field(None, max_length=500, description="郵寄地址")
    carrier_type: Optional[str] = Field(None, max_length=50, description="載具類型")
    carrier_number: Optional[str] = Field(None, max_length=100, description="載具號碼")
    tax_id: Optional[str] = Field(None, max_length=20, description="統一編號")

    @field_validator("tax_id")
    @classmethod
    def validate_tax_id(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.isdigit():
            raise ValueError("統一編號必須為數字")
        if v is not None and len(v) != 8:
            raise ValueError("統一編號必須為 8 碼")
        return v
