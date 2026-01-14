from modules.auth.domain.repositories.i_user_repository import IUserRepository
from modules.auth.use_cases.dtos import (
    LoginUserInputDTO,
    LoginUserOutputDTO
)
from core.exceptions import InvalidCredentialsError
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
        執行登入流程

        流程：
        1. 根據 email 查詢使用者
        2. 驗證使用者是否存在
        3. 驗證密碼是否正確
        4. 生成 JWT Access Token
        4.5. 根據 remember_me 決定是否生成 Refresh Token
        5. 轉換為 OutputDTO 並返回

        Args:
            input_dto: 登入輸入資料（包含 email, password, remember_me）

        Returns:
            LoginUserOutputDTO: 包含使用者資料、access token 和 refresh token（如果 remember_me=True）

        Raises:
            InvalidCredentialsError: 當使用者不存在或密碼錯誤時拋出
        """

        # Step 1: 根據 email 查詢使用者
        email = str(input_dto.email)
        user = await self.user_repository.get_by_email(email)

        # Step 2: 驗證使用者是否存在
        if user is None:
            # 使用通用錯誤訊息，不洩漏使用者是否存在的資訊
            raise InvalidCredentialsError()

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

