"""
Auth Command Use Cases

處理修改資料的業務邏輯（Commands）
"""
from modules.auth.domain.repositories.i_user_repository import IUserRepository
from modules.auth.domain.entity import UserEntity
from modules.auth.application.dtos import (
    RegisterRequestDTO,
    LoginRequestDTO,
    UserResponseDTO,
    LoginResponseDTO,
)
from core.exceptions import DuplicateEmailError, InvalidCredentialsError
from core.security import get_password_hash, create_access_token, create_refresh_token


class RegisterUserUseCase:
    """
    註冊使用者的業務邏輯

    職責：
    - 驗證 Email 是否已註冊
    - 加密密碼
    - 建立使用者
    """

    def __init__(self, user_repository: IUserRepository):
        """
        初始化 Use Case

        Args:
            user_repository: User Repository 介面實例
        """
        self.user_repository = user_repository

    async def execute(self, data: RegisterRequestDTO) -> UserResponseDTO:
        """
        執行註冊流程

        Args:
            data: 註冊請求的 Input DTO

        Returns:
            UserResponseDTO: 建立的使用者資料

        Raises:
            DuplicateEmailError: Email 已被註冊
        """
        # Step 1: 檢查 Email 是否已註冊
        email = str(data.email)
        if await self.user_repository.exists_by_email(email):
            raise DuplicateEmailError(email)

        # Step 2: 對密碼做雜湊處理
        hashed_password = get_password_hash(data.password)

        # Step 3: 建立 User Entity
        user = UserEntity(
            username=data.username,
            email=data.email,
            password_hash=hashed_password,
            is_active=True,
        )

        # Step 4: 透過 Repository 儲存
        created_user = await self.user_repository.create(user)

        # Step 5: Entity -> OutputDTO
        return UserResponseDTO(
            id=created_user.id,
            username=created_user.username,
            email=created_user.email,
            is_active=created_user.is_active,
            created_at=created_user.created_at,
            updated_at=created_user.updated_at,
        )


class LoginUserUseCase:
    """
    使用者登入的業務邏輯

    職責：
    - 驗證使用者憑證
    - 生成 JWT Token
    """

    def __init__(self, user_repository: IUserRepository):
        """
        初始化 Use Case

        Args:
            user_repository: User Repository 介面實例
        """
        self.user_repository = user_repository

    async def execute(self, data: LoginRequestDTO) -> LoginResponseDTO:
        """
        執行登入流程

        Args:
            data: 登入請求的 Input DTO

        Returns:
            LoginResponseDTO: 包含使用者資料和 Token

        Raises:
            InvalidCredentialsError: 憑證錯誤
        """
        # Step 1: 根據 Email 查詢使用者
        email = str(data.email)
        user = await self.user_repository.get_by_email(email)

        # Step 2: 驗證使用者是否存在
        if user is None:
            raise InvalidCredentialsError()

        # Step 3: 驗證密碼是否正確
        if not user.verify_password(data.password):
            raise InvalidCredentialsError()

        # Step 4: 生成 JWT Access Token
        token_data = {
            "sub": str(user.email),
            "user_id": str(user.id),
        }
        access_token = create_access_token(data=token_data)

        # Step 5: 根據 remember_me 決定是否生成 Refresh Token
        refresh_token = None
        if data.remember_me:
            refresh_token = create_refresh_token(data=token_data)

        # Step 6: 建立 User Response DTO
        user_dto = UserResponseDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

        # Step 7: 返回 Login Response DTO
        return LoginResponseDTO(
            access_token=access_token,
            token_type="bearer",
            refresh_token=refresh_token,
            user=user_dto,
        )

