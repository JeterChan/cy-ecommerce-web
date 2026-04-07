"""變更密碼 Use Case (登入狀態下)"""

from uuid import UUID
from modules.auth.domain.repository import IUserRepository
from modules.auth.domain.services.password_hasher import IPasswordHasher
from core.security import get_password_hash
from core.exceptions import UserNotFoundError, InvalidCredentialsError
import logging

logger = logging.getLogger(__name__)


class ChangePasswordUseCase:
    """變更密碼 Use Case"""

    def __init__(
        self, user_repository: IUserRepository, password_hasher: IPasswordHasher
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    async def execute(
        self, user_id: UUID, old_password: str, new_password: str
    ) -> bool:
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
        if not self.password_hasher.verify(old_password, user.password_hash):
            logger.warning(f"變更密碼失敗：舊密碼不正確 (id: {user_id})")
            raise InvalidCredentialsError("舊密碼不正確")

        # 更新密碼
        user.password_hash = get_password_hash(new_password)
        await self.user_repository.update(user)

        logger.info(f"使用者密碼變更成功 (id: {user_id})")
        return True
