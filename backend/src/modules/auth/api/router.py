from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import DuplicateEmailError
from src.infrastructure.database import get_db
from src.modules.auth.api.schemas import RegisterResponse, RegisterRequest
from src.modules.auth.infrastructure.repositories.user_repository import UserRepository
from src.modules.auth.use_cases import RegisterUserInputDTO, RegisterUserUseCase

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/api/v1/auth/register", status_code=status.HTTP_201_CREATED, response_model=RegisterResponse)
async def register_user(
        request: RegisterRequest,
        db: AsyncSession = Depends(get_db)
):
    """
        Register a new user and return the created user's data.
        
        Creates a user from the provided request and returns a RegisterResponse with the new user's id, username, email, activation flag, and creation timestamp.
        
        Returns:
            RegisterResponse: Contains `id`, `username`, `email`, `is_activate`, and `created_at` (ISO 8601 string or `None`).
        
        Raises:
            HTTPException: With status 400 Bad Request when the provided email is already in use.
        """
    try:
        # API Request -> Use Case Input DTO
        input_dto = RegisterUserInputDTO(
            username=request.username,
            email=request.email,
            password=request.password
        )

        # 建立 Repository 和 Use Case
        user_repo = UserRepository(db)
        use_case = RegisterUserUseCase(user_repo)

        # 執行 Use Case
        output_dto = await use_case.execute(input_dto)

        # Use Case Output DTO -> API response
        return RegisterResponse(
            id=output_dto.id,
            username=output_dto.username,
            email=output_dto.email,
            is_activate=output_dto.is_active,
            created_at=output_dto.created_at.isoformat() if output_dto.created_at else None,
        )

    except DuplicateEmailError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )