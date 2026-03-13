from pydantic import BaseModel, Field, ConfigDict

class ResetPasswordRequest(BaseModel):
    """重設密碼請求"""
    token: str = Field(..., description="重設 Token")
    new_password: str = Field(..., min_length=8, max_length=100, description="新密碼")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "abc123token",
                "new_password": "NewSecurePassword123!"
            }
        }
    )
