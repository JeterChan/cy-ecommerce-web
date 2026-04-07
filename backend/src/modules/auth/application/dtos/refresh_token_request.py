from pydantic import BaseModel, Field, ConfigDict


class RefreshTokenRequestDTO(BaseModel):
    refresh_token: str = Field(..., description="Refresh Token")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
        }
    )
