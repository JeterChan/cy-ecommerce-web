"""變更密碼 Use Case (登入狀態下)"""
from uuid import UUID
from modules.auth.domain.repositories.i_user_repository import IUserRepository
from core.security import get_password_hash
from core.exceptions import UserNotFoundError, InvalidCredentialsError
import logging

logger = logging.getLogger(__name__)

class ChangePasswordUseCase:
    """變更密碼 Use Case"""

    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: UUID, old_password: str, new_password: str) -> bool:
        """
        執行密碼變更

        Args:
            user_id: 使用者 ID
            old_password: 舊密碼
            new_password: 新密碼

        Returns:
            bool: 成功返回 True

        Raises:
            UserNotFoundError: 使用者不存在
            InvalidCredentialsError: 舊密碼錯誤
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"使用者不存在 (id: {user_id})")

        # 驗證舊密碼
        if not user.verify_password(old_password):
            logger.warning(f"變更密碼失敗：舊密碼不正確 (id: {user_id})")
            raise InvalidCredentialsError("舊密碼不正確")

        # 更新密碼
        user.password_hash = get_password_hash(new_password)
        await self.user_repository.update(user)
        
        logger.info(f"使用者密碼變更成功 (id: {user_id})")
        return True
