"""更新使用者個人檔案 Use Case"""
from uuid import UUID

from modules.auth.infrastructure.repositories.user_repository import UserRepository
from modules.auth.application.dtos.inputs import UpdateProfileRequest
from modules.auth.application.dtos.outputs import UpdateProfileResponse
from core.exceptions import UserNotFoundError


class UpdateProfileUseCase:
    """更新使用者個人檔案 Use Case"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(
        self, user_id: UUID, request: UpdateProfileRequest
    ) -> UpdateProfileResponse:
        """
        執行更新個人檔案

        只更新請求中有明確提供（非 None）的欄位。

        Args:
            user_id: 使用者 ID
            request: 更新個人檔案請求 DTO

        Returns:
            UpdateProfileResponse: 更新後的使用者個人檔案

        Raises:
            UserNotFoundError: 使用者不存在
        """
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"使用者不存在 (id: {user_id})")

        # 只更新有提供的欄位（Partial Update）
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

        return UpdateProfileResponse.from_entity(updated_user)
