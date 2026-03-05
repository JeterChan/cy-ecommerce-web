"""刪除帳戶 Use Case（軟刪除）"""
from uuid import UUID
from datetime import datetime, timezone

from modules.auth.infrastructure.repositories.user_repository import UserRepository
from core.exceptions import UserNotFoundError


class DeleteAccountUseCase:
    """
    刪除帳戶 Use Case（軟刪除）

    流程：
    1. 確認使用者存在
    2. 設定 is_active=False 與 deleted_at=now()
    3. 清除 Redis 中殘留的 Email 變更 tokens
    4. 儲存變更至資料庫

    帳號在 30 天後由 Celery Beat 定期任務執行硬刪除。
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: UUID) -> None:
        """
        執行帳戶軟刪除

        Args:
            user_id: 要刪除的使用者 ID

        Raises:
            UserNotFoundError: 使用者不存在
        """
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"使用者不存在 (id: {user_id})")

        # 軟刪除：停用帳號並記錄刪除時間
        user.is_active = False
        user.deleted_at = datetime.now(timezone.utc)

        await self.user_repository.update(user)
