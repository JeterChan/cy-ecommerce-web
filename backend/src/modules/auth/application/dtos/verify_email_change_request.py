from pydantic import BaseModel, Field
from .email_verify_type import EmailVerifyType


class VerifyEmailChangeRequest(BaseModel):
    token: str = Field(..., description="驗證 Token")
    type: EmailVerifyType = Field(..., description="驗證類型")
