"""取得使用者個人檔案 Use Case"""

from uuid import UUID

from modules.auth.domain.repository import IUserRepository
from modules.auth.application.dtos import UserProfileResponse
from core.exceptions import UserNotFoundError


class GetProfileUseCase:
    """取得使用者個人檔案 Use Case"""

    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: UUID) -> UserProfileResponse:
        """
        執行取得個人檔案邏輯

        Args:
            user_id: 使用者 ID

        Returns:
            UserProfileResponse: 使用者個人檔案資訊

        Raises:
            UserNotFoundError: 當使用者不存在時
        """
        # 從 repository 取得使用者
        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError(f"使用者不存在 (id: {user_id})")

        # 轉換為 DTO 並回傳
        return UserProfileResponse.from_entity(user)
