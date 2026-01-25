from modules.auth.domain.repositories.i_user_repository import IUserRepository
from modules.auth.use_cases.dtos import (
    RefreshTokenInputDTO,
    RefreshTokenOutputDTO
)
from core.exceptions import InvalidCredentialsError
from core.security import verify_token, create_access_token


class RefreshTokenUseCase:
    """
    刷新 Token Use Case

    職責：
    - 接收 RefreshTokenInputDTO，返回 RefreshTokenOutputDTO
    - 驗證 Refresh Token 的有效性
    - 生成新的 Access Token
    - 依賴 IUserRepository 抽象介面
    """

    def __init__(self, user_repository: IUserRepository):
        """
        Initialize the RefreshTokenUseCase with a user repository.
        
        Parameters:
            user_repository (IUserRepository): Repository used to fetch and validate users required by the use case.
        """
        self.user_repository = user_repository

    async def execute(self, input_dto: RefreshTokenInputDTO) -> RefreshTokenOutputDTO:
        """
        Refresh an access token using a valid refresh token.
        
        Parameters:
            input_dto (RefreshTokenInputDTO): Input DTO containing the `refresh_token` to validate and exchange.
        
        Returns:
            RefreshTokenOutputDTO: DTO containing the newly issued access token and its token type ("bearer").
        
        Raises:
            InvalidCredentialsError: If the refresh token is invalid, missing required claims, expired, the referenced user does not exist or is not active, or the token's user_id does not match the stored user id.
        """

        # Step 1: 驗證 Refresh Token
        payload = verify_token(input_dto.refresh_token, token_type="refresh")
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

        # 確保 Token 中的 user_id 與資料庫中的一致（防止 Token 偽造）
        if str(user.id) != user_id:
            raise InvalidCredentialsError()

        # Step 5: 生成新的 Access Token
        token_data = {
            "sub": str(user.email),
            "user_id": str(user.id),
        }
        access_token = create_access_token(data=token_data)

        # Step 6: 返回 OutputDTO
        return RefreshTokenOutputDTO(
            access_token=access_token,
            token_type="bearer"
        )
