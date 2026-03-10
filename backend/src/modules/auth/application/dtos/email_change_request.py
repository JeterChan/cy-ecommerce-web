from pydantic import BaseModel, EmailStr, Field

class EmailChangeRequest(BaseModel):
    new_email: EmailStr = Field(..., description="新的電子郵件地址")
    password: str = Field(..., min_length=8, description="目前密碼")
