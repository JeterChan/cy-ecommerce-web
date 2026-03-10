from pydantic import BaseModel, Field, ConfigDict

class DeleteAccountRequest(BaseModel):
    """刪除帳號請求"""
    password: str = Field(..., description="目前密碼（安全驗證）")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "password": "SecurePassword123!"
            }
        }
    )
