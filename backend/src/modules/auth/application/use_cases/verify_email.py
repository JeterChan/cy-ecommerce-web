"""驗證信箱 Use Case"""
from modules.auth.domain.repository import IUserRepository
from infrastructure.redis.token_manager import RedisTokenManager
from core.exceptions import UserNotFoundError
import logging

logger = logging.getLogger(__name__)

class VerifyEmailUseCase:
    """驗證信箱 Use Case"""

    def __init__(
        self, 
        user_repository: IUserRepository,
        token_manager: RedisTokenManager
    ):
        self.user_repository = user_repository
        self.token_manager = token_manager

    async def execute(self, token: str) -> bool:
        """
        執行信箱驗證

        Args:
            token: 驗證 Token

        Returns:
            bool: 驗證成功返回 True

        Raises:
            UserNotFoundError: 如果 Token 對應的使用者不存在
            ValueError: 如果 Token 無效或已過期
        """
        user_id = await self.token_manager.get_user_id_by_verify_token(token)
        if not user_id:
            logger.warning(f"信箱驗證失敗：Token 無效或已過期 (token: {token[:8]}...)")
            raise ValueError("驗證連結無效或已過期")

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            logger.error(f"信箱驗證失敗：找不到對應的使用者 (id: {user_id})")
            raise UserNotFoundError("使用者不存在")

        # 標記為已驗證並啟用
        user.is_verified = True
        user.is_active = True
        await self.user_repository.update(user)
        
        logger.info(f"使用者信箱驗證成功 (id: {user_id}, email: {user.email})")
        return True
