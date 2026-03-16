from modules.auth.domain.repositories.i_user_repository import IUserRepository
from modules.auth.domain.entities.UserEntity import UserEntity
from modules.auth.application.dtos import RegisterRequestDTO, UserResponseDTO
from infrastructure.redis.token_manager import RedisTokenManager
from infrastructure.tasks.email_tasks import send_registration_verification
from infrastructure.config import settings
from core.exceptions import DuplicateEmailError
from core.security import get_password_hash
import logging

logger = logging.getLogger(__name__)

class RegisterUserUseCase:
    """
    使用者註冊 Use Case
    """

    def __init__(self, user_repository: IUserRepository, token_manager: RedisTokenManager):
        self.user_repository = user_repository
        self.token_manager = token_manager

    async def execute(self, data: RegisterRequestDTO) -> UserResponseDTO:
        # step 1: check email
        email = str(data.email)
        if await self.user_repository.exists_by_email(email):
            logger.warning(f"註冊失敗：Email 已存在 (email: {email})")
            raise DuplicateEmailError(email)

        # step 2: 密碼雜湊
        hashed_password = get_password_hash(data.password)

        # step 3: 建立 User Entity
        user = UserEntity(
            username=data.username,
            email=data.email,
            password_hash=hashed_password,
            is_active=True,
            is_verified=False
        )

        # step 4: 儲存
        created_user = await self.user_repository.create(user)
        logger.info(f"使用者帳號已建立 (id: {created_user.id}, email: {created_user.email})")

        # step 5: 生成驗證 Token 並存入 Redis
        token = self.token_manager.generate_token()
        await self.token_manager.store_verification_token(str(created_user.id), token)

        # step 6: 發送驗證信
        verification_url = f"{settings.FRONTEND_URL}/email-verify?token={token}"
        send_registration_verification.delay(
            to_email=str(created_user.email),
            username=created_user.username,
            verification_url=verification_url
        )
        logger.info(f"已發送註冊驗證信至 {created_user.email}")

        return UserResponseDTO.model_validate(created_user)
