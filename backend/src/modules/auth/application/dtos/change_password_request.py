from pydantic import BaseModel, Field, ConfigDict

class ChangePasswordRequest(BaseModel):
    """變更密碼請求 (登入狀態)"""
    old_password: str = Field(..., description="舊密碼")
    new_password: str = Field(..., min_length=8, max_length=100, description="新密碼")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "old_password": "OldSecurePassword123!",
                "new_password": "NewSecurePassword456!"
            }
        }
    )
