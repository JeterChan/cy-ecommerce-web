"""重設密碼 Use Case"""
from modules.auth.domain.repository import IUserRepository
from infrastructure.redis.token_manager import RedisTokenManager
from core.security import get_password_hash
from core.exceptions import UserNotFoundError
import logging

logger = logging.getLogger(__name__)

class ResetPasswordUseCase:
    """重設密碼 Use Case"""

    def __init__(
        self, 
        user_repository: IUserRepository,
        token_manager: RedisTokenManager
    ):
        self.user_repository = user_repository
        self.token_manager = token_manager

    async def execute(self, token: str, new_password: str) -> bool:
        """
        執行密碼重設

        Args:
            token: 重設 Token
            new_password: 新密碼（明文）

        Returns:
            bool: 成功返回 True

        Raises:
            ValueError: 如果 Token 無效或已過期
            UserNotFoundError: 如果使用者不存在
        """
        user_id = await self.token_manager.get_user_id_by_reset_token(token)
        if not user_id:
            logger.warning(f"密碼重設失敗：Token 無效或已過期 (token: {token[:8]}...)")
            raise ValueError("重設連結無效或已過期")

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            logger.error(f"密碼重設失敗：找不到使用者 (id: {user_id})")
            raise UserNotFoundError("使用者不存在")

        # 更新密碼雜湊
        user.password_hash = get_password_hash(new_password)
        await self.user_repository.update(user)
        
        logger.info(f"密碼重設成功 (id: {user_id}, email: {user.email})")
        return True
