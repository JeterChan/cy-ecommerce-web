from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RegisterRequestDTO(BaseModel):
    email: EmailStr = Field(..., description="使用者信箱")
    username: str = Field(..., min_length=3, max_length=50, description="使用者名稱")
    password: str = Field(
        ..., min_length=8, max_length=100, description="密碼 (8-100 字元)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "username": "john_doe",
                "password": "SecureP@ssw0rd",
            }
        }
    )
