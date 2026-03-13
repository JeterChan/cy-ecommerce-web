"""忘記密碼 Use Case"""
from modules.auth.domain.repositories.i_user_repository import IUserRepository
from infrastructure.redis.token_manager import RedisTokenManager
from infrastructure.tasks.email_tasks import send_password_reset
from infrastructure.config import settings
from core.exceptions import UserNotRegisteredError
import logging

logger = logging.getLogger(__name__)

class ForgotPasswordUseCase:
    """忘記密碼 Use Case"""

    def __init__(
        self, 
        user_repository: IUserRepository,
        token_manager: RedisTokenManager
    ):
        self.user_repository = user_repository
        self.token_manager = token_manager

    async def execute(self, email: str) -> bool:
        """
        處理忘記密碼請求

        Args:
            email: 使用者 Email

        Returns:
            bool: 請求成功返回 True

        Raises:
            UserNotRegisteredError: 當 Email 未註冊時拋出
        """
        user = await self.user_repository.get_by_email(email)
        
        # 如果 Email 不存在則拋出異常
        if not user:
            logger.info(f"忘記密碼請求失敗：Email 未註冊 (email: {email})")
            raise UserNotRegisteredError(email)

        # 生成 Token 並存入 Redis
        token = self.token_manager.generate_token()
        await self.token_manager.store_reset_token(str(user.id), token)

        # 發送重設信 (非同步)
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        send_password_reset.delay(
            to_email=str(user.email),
            username=user.username,
            reset_url=reset_url
        )
        
        logger.info(f"已發送密碼重設信至 {user.email} (id: {user.id})")
        return True
