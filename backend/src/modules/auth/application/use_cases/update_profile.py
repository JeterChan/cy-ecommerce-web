"""更新使用者個人檔案 Use Case"""

from uuid import UUID
from modules.auth.domain.repository import IUserRepository
from modules.auth.application.dtos import UpdateProfileRequest, UpdateProfileResponse
from core.exceptions import UserNotFoundError, ValidationError
import logging

logger = logging.getLogger(__name__)


class UpdateProfileUseCase:
    """更新使用者個人檔案 Use Case"""

    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def execute(
        self, user_id: UUID, request: UpdateProfileRequest
    ) -> UpdateProfileResponse:
        """
        執行更新個人檔案
        """
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"使用者不存在 (id: {user_id})")

        # 處理使用者名稱變更
        if request.username is not None and request.username != user.username:
            if await self.user_repository.exists_by_username(request.username):
                logger.warning(
                    f"更新個人檔案失敗：使用者名稱已存在 (username: {request.username})"
                )
                raise ValidationError("使用者名稱已存在")
            user.username = request.username
            logger.info(
                f"使用者名稱已變更 (id: {user_id}, new_username: {request.username})"
            )

        # 更新其他欄位 (Partial Update)
        if request.phone is not None:
            user.phone = request.phone
        if request.address is not None:
            user.address = request.address
        if request.carrier_type is not None:
            user.carrier_type = request.carrier_type
        if request.carrier_number is not None:
            user.carrier_number = request.carrier_number
        if request.tax_id is not None:
            user.tax_id = request.tax_id

        updated_user = await self.user_repository.update(user)
        logger.info(f"使用者個人檔案已更新 (id: {user_id})")

        return UpdateProfileResponse.from_entity(updated_user)
