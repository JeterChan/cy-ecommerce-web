from modules.auth.domain.repository import IUserRepository
from modules.auth.domain.services.password_hasher import IPasswordHasher
from modules.auth.application.dtos import LoginRequestDTO, LoginResponseDTO, UserResponseDTO
from core.exceptions import InvalidCredentialsError, EmailNotVerifiedError, UserNotRegisteredError
from core.security import create_access_token, create_refresh_token
import logging

logger = logging.getLogger(__name__)

class LoginUserUseCase:
    """
    使用者登入 Use Case
    """

    def __init__(self, user_repository: IUserRepository, password_hasher: IPasswordHasher):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    async def execute(self, data: LoginRequestDTO) -> LoginResponseDTO:
        # Step 1: 查詢使用者
        email = str(data.email)
        user = await self.user_repository.get_by_email(email)

        # Step 2: 驗證使用者是否存在
        if user is None:
            logger.warning(f"登入失敗：Email 未註冊 (email: {email})")
            raise UserNotRegisteredError(email)

        # Step 3: 驗證密碼
        if not self.password_hasher.verify(data.password, user.password_hash):
            logger.warning(f"登入失敗：密碼錯誤 (email: {email})")
            raise InvalidCredentialsError()

        # Step 3.5: 驗證信箱
        if not user.is_verified:
            logger.warning(f"登入失敗：信箱未驗證 (email: {email})")
            raise EmailNotVerifiedError()

        # Step 4: 生成 JWT Tokens
        token_data = {
            "sub": str(user.email),
            "user_id": str(user.id),
        }
        access_token = create_access_token(data=token_data)

        refresh_token = None
        if data.remember_me:
            refresh_token = create_refresh_token(data=token_data)

        logger.info(f"使用者登入成功 (id: {user.id}, email: {user.email})")

        user_dto = UserResponseDTO.model_validate(user)

        return LoginResponseDTO(
            access_token=access_token,
            token_type="bearer",
            refresh_token=refresh_token,
            user=user_dto,
        )
