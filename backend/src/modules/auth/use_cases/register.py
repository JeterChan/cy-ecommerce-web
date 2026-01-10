from src.modules.auth.domain.repositories.i_user_repository import IUserRepository
from src.modules.auth.domain.entities import UserEntity
from src.modules.auth.use_cases.dtos import (
    RegisterUserInputDTO,
    RegisterUserOutputDTO
)
from src.core.exceptions import DuplicateEmailError
from src.core.security import get_password_hash

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
        """
        Initialize the use case with its user repository dependency.
        
        Parameters:
            user_repository (IUserRepository): Repository providing user persistence and lookup operations required by the use case.
        """
        self.user_repository = user_repository

    async def execute(self, input_dto: RegisterUserInputDTO) -> RegisterUserOutputDTO:
        """
        Register a new user and return a DTO representing the created user.
        
        Parameters:
            input_dto (RegisterUserInputDTO): Input data with `username`, `email`, and `password`.
        
        Returns:
            RegisterUserOutputDTO: DTO containing the created user's `id`, `username`, `email`, `is_active`, and `created_at`.
        
        Raises:
            DuplicateEmailError: If the provided email is already registered.
        """
        # step 1: check email register or not
        if await self.user_repository.exists_by_email(input_dto.email):
            raise DuplicateEmailError(
                f"Email {input_dto.email} is already registered"
            )
        # step 2: 對密碼做雜湊處理
        hashed_password = get_password_hash(input_dto.password)

        # step 3: 建立 User Entity
        user = UserEntity(
            username=input_dto.username,
            email=input_dto.email,
            password_hash=hashed_password,
            is_activate=True,
        )

        # step 4: 透過 Repository 儲存
        created_user = await self.user_repository.create(user)

        # step 5: Entity -> OutputDTO
        return RegisterUserOutputDTO(
            id=created_user.id,
            username=created_user.username,
            email=created_user.email,
            is_active=created_user.is_activate,  # Entity 使用 is_activate
            created_at=created_user.created_at,
        )