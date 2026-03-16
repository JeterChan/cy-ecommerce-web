from pydantic import BaseModel, EmailStr, Field, ConfigDict

class ForgotPasswordRequest(BaseModel):
    """忘記密碼請求"""
    email: EmailStr = Field(..., description="註冊時的電子郵件")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com"
            }
        }
    )
