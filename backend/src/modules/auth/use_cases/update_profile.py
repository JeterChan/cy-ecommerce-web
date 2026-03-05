"""更新使用者個人檔案 Use Case"""
from uuid import UUID

from modules.auth.infrastructure.repositories.user_repository import UserRepository
from modules.auth.use_cases.dtos import UpdateProfileInputDTO, UpdateProfileOutputDTO


class UpdateProfileUseCase:
    """更新使用者個人檔案 Use Case"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: UUID, input_dto: UpdateProfileInputDTO) -> UpdateProfileOutputDTO:
        """
        執行更新個人檔案

        Args:
            user_id: 使用者 ID
            input_dto: 更新個人檔案輸入 DTO

        Returns:
            UpdateProfileOutputDTO: 更新後的使用者資料

        Raises:
            UserNotFoundError: 使用者不存在
        """
        # 取得使用者
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            from core.exceptions import UserNotFoundError
            raise UserNotFoundError(f"使用者不存在 (id: {user_id})")

        # 更新欄位（只更新有提供的欄位）
        if input_dto.phone is not None:
            user.phone = input_dto.phone
        if input_dto.address is not None:
            user.address = input_dto.address
        if input_dto.carrier_type is not None:
            user.carrier_type = input_dto.carrier_type
        if input_dto.carrier_number is not None:
            user.carrier_number = input_dto.carrier_number
        if input_dto.tax_id is not None:
            user.tax_id = input_dto.tax_id

        # 儲存更新
        updated_user = await self.user_repository.update(user)

        # 轉換為 OutputDTO
        return UpdateProfileOutputDTO(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
            is_active=updated_user.is_active,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
            phone=updated_user.phone,
            address=updated_user.address,
            carrier_type=updated_user.carrier_type,
            carrier_number=updated_user.carrier_number,
            tax_id=updated_user.tax_id,
        )

