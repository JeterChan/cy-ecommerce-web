"""
Auth DTOs (Data Transfer Objects)

區分 Input 和 Output DTOs 以提高程式碼清晰度
"""
from .inputs import (
    RegisterRequestDTO,
    LoginRequestDTO,
    RefreshTokenRequestDTO,
    UpdateProfileRequest,
    EmailChangeRequest,
    VerifyEmailChangeRequest,
    EmailVerifyType,
)
from .outputs import (
    UserResponseDTO,
    TokenResponseDTO,
    LoginResponseDTO,
    UserProfileResponse,
    UpdateProfileResponse,
)

__all__ = [
    # Input DTOs
    "RegisterRequestDTO",
    "LoginRequestDTO",
    "RefreshTokenRequestDTO",
    "UpdateProfileRequest",
    "EmailChangeRequest",
    "VerifyEmailChangeRequest",
    "EmailVerifyType",

    # Output DTOs
    "UserResponseDTO",
    "TokenResponseDTO",
    "LoginResponseDTO",
    "UserProfileResponse",
    "UpdateProfileResponse",
]

