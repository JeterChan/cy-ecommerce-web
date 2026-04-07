from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class TokenResponseDTO(BaseModel):
    """Token 回應的 DTO"""

    access_token: str = Field(..., description="JWT Access Token")
    token_type: str = Field(default="bearer", description="Token 類型")
    refresh_token: Optional[str] = Field(None, description="JWT Refresh Token (可選)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "refresh_token": None,
            }
        }
    )
