from modules.auth.domain.repositories.i_user_repository import IUserRepository
from modules.auth.use_cases.dtos import (
    LoginUserInputDTO,
    LoginUserOutputDTO
)
from core.exceptions import InvalidCredentialsError, UserNotRegisteredError
from core.security import create_access_token, create_refresh_token


class LoginUserUseCase:
    """
    使用者登入 Use Case

    職責：
    - 接收 LoginUserInputDTO，返回 LoginUserOutputDTO
    - 實作登入業務邏輯（驗證憑證、生成 Token）
    - 依賴 IUserRepository 抽象介面
    """

    def __init__(self, user_repository: IUserRepository):
        """
        初始化 Use Case

        Args:
            user_repository: User Repository 介面實例
        """
        self.user_repository = user_repository

    async def execute(self, input_dto: LoginUserInputDTO) -> LoginUserOutputDTO:
        """
        Authenticate a user, issue JWT tokens, and return the user data and tokens.
        
        Parameters:
            input_dto (LoginUserInputDTO): Login input containing `email`, `password`, and `remember_me` flag.
        
        Returns:
            LoginUserOutputDTO: User fields (id, username, email, is_active, created_at, updated_at), an access token and token_type "bearer"; includes a refresh_token only when `remember_me` is true.
        
        Raises:
            UserNotRegisteredError: If the user with the provided email does not exist.
            InvalidCredentialsError: If the provided password is incorrect.
        """

        # Step 1: 根據 email 查詢使用者
        email = str(input_dto.email)
        user = await self.user_repository.get_by_email(email)

        # Step 2: 驗證使用者是否存在
        if user is None:
            # 明確告知使用者信箱未註冊
            raise UserNotRegisteredError(email)

        # Step 3: 驗證密碼是否正確
        if not user.verify_password(input_dto.password):
            # 使用通用錯誤訊息
            raise InvalidCredentialsError()

        # Step 4: 生成 JWT Access Token
        token_data = {
            "sub": str(user.email),  # Subject: 使用者識別（使用 email）
            "user_id": str(user.id),  # 使用者 ID
        }
        access_token = create_access_token(data=token_data)

        # Step 4.5: 根據 remember_me 決定是否生成 Refresh Token
        refresh_token = None
        if input_dto.remember_me:
            refresh_token = create_refresh_token(data=token_data)

        # Step 5: 轉換為 OutputDTO
        return LoginUserOutputDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,  # Entity 使用 is_active
            created_at=user.created_at,
            updated_at=user.updated_at,
            access_token=access_token,
            token_type="bearer",
            refresh_token=refresh_token if input_dto.remember_me else None,
        )
