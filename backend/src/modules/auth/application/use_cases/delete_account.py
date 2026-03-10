"""刪除帳戶 Use Case（軟刪除）"""
from uuid import UUID
from datetime import datetime, timezone
from modules.auth.domain.repositories.i_user_repository import IUserRepository
from core.exceptions import UserNotFoundError, InvalidCredentialsError
import logging

logger = logging.getLogger(__name__)

class DeleteAccountUseCase:
    """
    刪除帳戶 Use Case（軟刪除）

    流程：
    1. 驗證目前密碼
    2. 設定 is_active=False 與 deleted_at=now()
    3. 儲存變更至資料庫
    """

    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: UUID, password: str) -> None:
        """
        執行帳戶軟刪除

        Args:
            user_id: 使用者 ID
            password: 目前密碼（用於安全驗證）

        Raises:
            UserNotFoundError: 使用者不存在
            InvalidCredentialsError: 密碼驗證失敗
        """
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"使用者不存在 (id: {user_id})")

        # 驗證密碼
        if not user.verify_password(password):
            logger.warning(f"帳號刪除失敗：密碼驗證失敗 (id: {user_id})")
            raise InvalidCredentialsError("密碼驗證失敗，無法刪除帳號")

        # 軟刪除：停用帳號並記錄刪除時間
        user.is_active = False
        user.deleted_at = datetime.now(timezone.utc)
        
        # 依照 Plan，釋放 Email 資源 (這裡可以選擇清空 email 或加前綴，以利重新註冊)
        # 決策：在軟刪除時保留 email 但在 Unique 檢查時排除已刪除帳號 (已在 UserRepository 實作)
        # 或者這裡將 email 加上刪除標記以釋出原始 email
        original_email = str(user.email)
        user.email = f"deleted_{user.id}_{original_email}"

        await self.user_repository.update(user)
        
        logger.info(f"帳號已成功軟刪除 (id: {user_id}, original_email: {original_email})")
