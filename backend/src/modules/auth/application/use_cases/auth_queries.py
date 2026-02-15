"""
Auth Query Use Cases

處理查詢資料的業務邏輯（Queries）
"""
from modules.auth.domain.repositories.i_user_repository import IUserRepository
from modules.auth.application.dtos import (
    RefreshTokenRequestDTO,
    TokenResponseDTO,
)
from core.exceptions import InvalidCredentialsError
from core.security import verify_token, create_access_token


class RefreshTokenUseCase:
    """
    刷新 Token 的業務邏輯

    職責：
    - 驗證 Refresh Token
    - 生成新的 Access Token
    """

    def __init__(self, user_repository: IUserRepository):
        """
        初始化 Use Case

        Args:
            user_repository: User Repository 介面實例
        """
        self.user_repository = user_repository

    async def execute(self, data: RefreshTokenRequestDTO) -> TokenResponseDTO:
        """
        執行刷新 Token 流程

        Args:
            data: 刷新 Token 請求的 Input DTO

        Returns:
            TokenResponseDTO: 新的 Access Token

        Raises:
            InvalidCredentialsError: Token 無效或使用者不存在
        """
        # Step 1: 驗證 Refresh Token
        payload = verify_token(data.refresh_token, token_type="refresh")
        if payload is None:
            raise InvalidCredentialsError()

        # Step 2: 從 Token payload 中取得使用者資訊
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")

        if not email or not user_id:
            raise InvalidCredentialsError()

        # Step 3: 查詢使用者
        user = await self.user_repository.get_by_email(email)

        if user is None:
            raise InvalidCredentialsError()

        # Step 4: 驗證使用者狀態
        if not user.is_active:
            raise InvalidCredentialsError()

        # 確保 Token 中的 user_id 與資料庫中的一致
        if str(user.id) != user_id:
            raise InvalidCredentialsError()

        # Step 5: 生成新的 Access Token
        token_data = {
            "sub": str(user.email),
            "user_id": str(user.id),
        }
        access_token = create_access_token(data=token_data)

        # Step 6: 返回 TokenResponseDTO
        return TokenResponseDTO(
            access_token=access_token,
            token_type="bearer"
        )

