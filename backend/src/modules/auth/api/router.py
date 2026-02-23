from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import InvalidCredentialsError, UserNotRegisteredError
from core.security import verify_token
from infrastructure.database import get_db
from modules.auth.api.schemas import (
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    ProfileUpdateRequest,
    UserProfileResponse,
)
from modules.auth.infrastructure.repositories.user_repository import UserRepository
from modules.auth.use_cases import (
    RegisterUserInputDTO,
    RegisterUserUseCase,
    LoginUserInputDTO,
    LoginUserUseCase,
    RefreshTokenInputDTO,
    RefreshTokenUseCase,
    UpdateProfileInputDTO,
    UpdateProfileUseCase,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# HTTP Bearer 認證 scheme
security = HTTPBearer()


# ==================== Dependency Functions ====================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    取得當前登入的使用者

    從 HTTP Authorization Header 中解析 JWT Token，驗證並返回使用者資料

    Args:
        credentials: HTTP Bearer Token
        db: 資料庫 Session

    Returns:
        UserEntity: 當前使用者

    Raises:
        HTTPException 401: Token 無效或過期
        HTTPException 404: 使用者不存在
    """
    token = credentials.credentials

    # 驗證 Token
    payload = verify_token(token, token_type="access")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無效或過期的 Token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 從 Token 中取得使用者 email
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 缺少使用者資訊",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"[Auth] 從 token 獲取的 email: {email}")
    print(f"[Auth] Token payload: {payload}")

    # 查詢使用者
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(email)

    print(f"[Auth] 資料庫查詢結果: {user}")

    if user is None:
        print(f"[Auth] ❌ 使用者不存在! Email: {email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"使用者不存在 (email: {email})"
        )

    print(f"[Auth] ✅ 使用者查詢成功: {user.email}")
    return user


# ==================== API Endpoints ====================

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponse)
async def register_user(
        request: RegisterRequest,
        db: AsyncSession = Depends(get_db)
):
    """
        Register a new user and return the created user's public profile.
        
        Parameters:
            request (RegisterRequest): Registration data containing `email`, `username`, and `password`.
        
        Returns:
            RegisterResponse: The created user's details (`id`, `username`, `email`, `is_active`, `created_at`, `updated_at`).
        """
    # API schema -> Use Case DTO
    input_dto = RegisterUserInputDTO(
        email=request.email,
        username=request.username,
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
        is_active=output_dto.is_active,
        created_at=output_dto.created_at,
        updated_at=output_dto.updated_at,
    )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse
)
async def login_user(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate a user and return access/refresh tokens along with the user's profile.
    
    Parameters:
        request (LoginRequest): Login credentials (`email`, `password`) and `remember_me` flag.
        db (AsyncSession): Database session.
    
    Returns:
        LoginResponse: Contains `access_token`, `token_type`, optional `refresh_token`, and the authenticated user's information.
    
    Raises:
        HTTPException (401): If the provided credentials are invalid.
    """

    # 轉換為 InputDTO
    input_dto = LoginUserInputDTO(
        email=request.email,
        password=request.password,
        remember_me=request.remember_me
    )

    # 建立 Repository 和 Use Case
    user_repo = UserRepository(db)
    use_case = LoginUserUseCase(user_repo)

    try:
        # 執行 Use Case
        output_dto = await use_case.execute(input_dto)

        # Use Case Output DTO -> API Response
        return LoginResponse(
            access_token=output_dto.access_token,
            token_type=output_dto.token_type,
            refresh_token=output_dto.refresh_token,
            user=RegisterResponse(
                id=output_dto.id,
                username=output_dto.username,
                email=output_dto.email,
                is_active=output_dto.is_active,
                created_at=output_dto.created_at,
                updated_at=output_dto.updated_at,
            )
        )
    except UserNotRegisteredError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse
)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh the access token using a refresh token.
    
    Parameters:
        request (RefreshTokenRequest): Request containing the refresh token to validate.
    
    Returns:
        TokenResponse: New access token and token type; `refresh_token` is None.
    
    Raises:
        HTTPException: 401 Unauthorized if the refresh token is invalid or expired.
    """
    # 轉換為 InputDTO
    input_dto = RefreshTokenInputDTO(
        refresh_token=request.refresh_token
    )

    # 建立 Repository 和 Use Case
    user_repo = UserRepository(db)
    use_case = RefreshTokenUseCase(user_repo)

    try:
        # 執行 Use Case
        output_dto = await use_case.execute(input_dto)

        # Use Case Output DTO -> API Response
        return TokenResponse(
            access_token=output_dto.access_token,
            token_type=output_dto.token_type,
            refresh_token=None  # 不返回新的 refresh_token，保持原有的有效
        )
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserProfileResponse
)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """
    Return the currently authenticated user's full profile including personal information.

    Returns:
        UserProfileResponse: The user's complete profile including phone, address, carrier, and tax_id.
    """
    return UserProfileResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        phone=current_user.phone,
        address=current_user.address,
        carrier_type=current_user.carrier_type,
        carrier_number=current_user.carrier_number,
        tax_id=current_user.tax_id,
    )


@router.patch(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserProfileResponse
)
async def update_current_user_profile(
    request: ProfileUpdateRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update the currently authenticated user's profile information.

    Parameters:
        request (ProfileUpdateRequest): Profile data to update (phone, address, carrier info, tax_id).

    Returns:
        UserProfileResponse: Updated user profile.
    """
    # 轉換為 InputDTO
    input_dto = UpdateProfileInputDTO(
        phone=request.phone,
        address=request.address,
        carrier_type=request.carrier_type,
        carrier_number=request.carrier_number,
        tax_id=request.tax_id,
    )

    # 建立 Repository 和 Use Case
    user_repo = UserRepository(db)
    use_case = UpdateProfileUseCase(user_repo)

    # 執行 Use Case
    output_dto = await use_case.execute(current_user.id, input_dto)

    # 轉換為 API Response
    return UserProfileResponse(
        id=output_dto.id,
        username=output_dto.username,
        email=output_dto.email,
        is_active=output_dto.is_active,
        created_at=output_dto.created_at,
        updated_at=output_dto.updated_at,
        phone=output_dto.phone,
        address=output_dto.address,
        carrier_type=output_dto.carrier_type,
        carrier_number=output_dto.carrier_number,
        tax_id=output_dto.tax_id,
    )

