from modules.auth.domain.repositories.i_user_repository import IUserRepository
from modules.auth.application.dtos import RefreshTokenRequestDTO, TokenResponseDTO
from core.exceptions import InvalidCredentialsError
from core.security import verify_token, create_access_token


class RefreshTokenUseCase:
    """
    刷新 Token Use Case
    """

    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def execute(self, data: RefreshTokenRequestDTO) -> TokenResponseDTO:
        # Step 1: 驗證 Refresh Token
        payload = verify_token(data.refresh_token, token_type="refresh")
        if payload is None:
            raise InvalidCredentialsError()

        # Step 2: 取得使用者資訊
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")

        if not email or not user_id:
            raise InvalidCredentialsError()

        # Step 3: 查詢使用者
        user = await self.user_repository.get_by_email(email)

        if user is None or not user.is_active:
            raise InvalidCredentialsError()

        # Step 4: 生成新的 Access Token
        token_data = {
            "sub": str(user.email),
            "user_id": str(user.id),
        }
        access_token = create_access_token(data=token_data)

        return TokenResponseDTO(
            access_token=access_token,
            token_type="bearer"
        )
