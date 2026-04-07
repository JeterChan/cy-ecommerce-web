from pydantic import Field
from .token_response import TokenResponseDTO
from .user_response import UserResponseDTO


class LoginResponseDTO(TokenResponseDTO):
    """登入回應的 DTO"""

    user: UserResponseDTO = Field(..., description="使用者資料")
