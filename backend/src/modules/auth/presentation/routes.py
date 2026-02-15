"""
Auth API Routes

定義 Auth 模組的 HTTP API 端點
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import get_db
from core.security import verify_token
from core.exceptions import InvalidCredentialsError, DuplicateEmailError

from modules.auth.application.use_cases import (
    RegisterUserUseCase,
    LoginUserUseCase,
    RefreshTokenUseCase,
)
from modules.auth.application.dtos import (
    RegisterRequestDTO,
    LoginRequestDTO,
    RefreshTokenRequestDTO,
    UserResponseDTO,
    LoginResponseDTO,
    TokenResponseDTO,
)
from modules.auth.infrastructure.repositories.user_repository import UserRepository
from modules.auth.domain.entity import UserEntity


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
security = HTTPBearer()


# ==================== Dependency Functions ====================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserEntity:
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

    # 查詢使用者
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="使用者不存在"
        )

    return user


# ==================== API Endpoints ====================

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseDTO,
    summary="註冊新使用者",
    description="建立新的使用者帳號"
)
async def register_user(
    data: RegisterRequestDTO,
    db: AsyncSession = Depends(get_db)
) -> UserResponseDTO:
    """
    註冊新使用者

    - **email**: 使用者信箱（必填，唯一）
    - **username**: 使用者名稱（必填，3-50 字元）
    - **password**: 密碼（必填，8-100 字元）
    """
    try:
        # 建立 Repository 和 Use Case
        user_repo = UserRepository(db)
        use_case = RegisterUserUseCase(user_repo)

        # 執行 Use Case
        user_dto = await use_case.execute(data)

        return user_dto

    except DuplicateEmailError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponseDTO,
    summary="使用者登入",
    description="使用 Email 和密碼登入"
)
async def login_user(
    data: LoginRequestDTO,
    db: AsyncSession = Depends(get_db)
) -> LoginResponseDTO:
    """
    使用者登入

    - **email**: 使用者信箱
    - **password**: 密碼
    - **remember_me**: 是否記住我（會生成 Refresh Token）
    """
    try:
        # 建立 Repository 和 Use Case
        user_repo = UserRepository(db)
        use_case = LoginUserUseCase(user_repo)

        # 執行 Use Case
        login_dto = await use_case.execute(data)

        return login_dto

    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponseDTO,
    summary="刷新 Access Token",
    description="使用 Refresh Token 取得新的 Access Token"
)
async def refresh_token(
    data: RefreshTokenRequestDTO,
    db: AsyncSession = Depends(get_db)
) -> TokenResponseDTO:
    """
    刷新 Access Token

    - **refresh_token**: Refresh Token
    """
    try:
        # 建立 Repository 和 Use Case
        user_repo = UserRepository(db)
        use_case = RefreshTokenUseCase(user_repo)

        # 執行 Use Case
        token_dto = await use_case.execute(data)

        return token_dto

    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponseDTO,
    summary="取得當前使用者資訊",
    description="取得當前登入使用者的資料"
)
async def get_me(
    current_user: UserEntity = Depends(get_current_user)
) -> UserResponseDTO:
    """
    取得當前使用者資訊

    需要在 Header 中提供有效的 JWT Token：
    Authorization: Bearer <access_token>
    """
    return UserResponseDTO(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )

