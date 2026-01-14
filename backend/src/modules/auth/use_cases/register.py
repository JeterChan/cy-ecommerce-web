from modules.auth.domain.repositories.i_user_repository import IUserRepository
from modules.auth.domain.entity import UserEntity
from modules.auth.use_cases.dtos import (
    RegisterUserInputDTO,
    RegisterUserOutputDTO
)
from core.exceptions import DuplicateEmailError
from core.security import get_password_hash

class RegisterUserUseCase:
    """
        使用者註冊範例
        職責：
        - 接收 InputDTO，返回 OutputDTO
        - 實作註冊業務邏輯
        - 依賴 IUserRepository 抽象介面
        - 處理密碼加密等業務規則
    """

    # Dependency Injection
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def execute(self, input_dto: RegisterUserInputDTO) -> RegisterUserOutputDTO:
        """
        流程：
        1. 驗證電子郵件是否已註冊
        2. 對密碼進行雜湊處理
        3. 建立 User Entity
        4. 透過 Repository 儲存到資料庫
        5. 轉換為 OutputDTO
        """
        # step 1: check email register or not
        email = str(input_dto.email)
        if await self.user_repository.exists_by_email(email):
            raise DuplicateEmailError(email)
        # step 2: 對密碼做雜湊處理
        hashed_password = get_password_hash(input_dto.password)

        # step 3: 建立 User Entity
        user = UserEntity(
            username=input_dto.username,
            email=input_dto.email,
            password_hash=hashed_password,
            is_active=True,
        )

        # step 4: 透過 Repository 儲存
        created_user = await self.user_repository.create(user)

        # step 5: Entity -> OutputDTO
        return RegisterUserOutputDTO(
            id=created_user.id,
            username=created_user.username,
            email=created_user.email,
            is_active=created_user.is_active,  # Entity 使用 is_active
            created_at=created_user.created_at,
            updated_at=created_user.updated_at,
        )

