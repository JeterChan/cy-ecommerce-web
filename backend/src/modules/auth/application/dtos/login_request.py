from pydantic import BaseModel, EmailStr, Field, ConfigDict


class LoginRequestDTO(BaseModel):
    email: EmailStr = Field(..., description="使用者信箱")
    password: str = Field(..., min_length=8, description="密碼")
    remember_me: bool = Field(False, description="記住我")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecureP@ssw0rd",
                "remember_me": True,
            }
        }
    )
