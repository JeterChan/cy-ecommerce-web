"""
Auth DTOs (Data Transfer Objects)

區分 Input 和 Output DTOs 以提高程式碼清晰度
"""
from .inputs import (
    RegisterRequestDTO,
    LoginRequestDTO,
    RefreshTokenRequestDTO,
)
from .outputs import (
    UserResponseDTO,
    TokenResponseDTO,
    LoginResponseDTO,
)

__all__ = [
    # Input DTOs
    "RegisterRequestDTO",
    "LoginRequestDTO",
    "RefreshTokenRequestDTO",

    # Output DTOs
    "UserResponseDTO",
    "TokenResponseDTO",
    "LoginResponseDTO",
]

