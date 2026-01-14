from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import InvalidCredentialsError
from core.security import verify_token
from infrastructure.database import get_db
from modules.auth.api.schemas import (
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest
)
from modules.auth.infrastructure.repositories.user_repository import UserRepository
from modules.auth.use_cases import (
    RegisterUserInputDTO,
    RegisterUserUseCase,
    LoginUserInputDTO,
    LoginUserUseCase,
    RefreshTokenInputDTO,
    RefreshTokenUseCase
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
    response_model=RegisterResponse)
async def register_user(
        request: RegisterRequest,
        db: AsyncSession = Depends(get_db)
):
    """
    註冊新使用者 API

    依賴注入流程：
    1. FastAPI 驗證 RegisterRequest
    2. 轉換為 RegisterUserInputDTO
    3. 注入 AsyncSession
    4. 建立 UserRepository
    5. 建立 RegisterUserUseCase
    6. 執行業務邏輯
    7. 返回 RegisterResponse
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
    使用者登入 API

    依賴注入流程：
    1. FastAPI 驗證 LoginRequest
    2. 轉換為 LoginUserInputDTO
    3. 注入 AsyncSession
    4. 建立 UserRepository
    5. 建立 LoginUserUseCase
    6. 執行登入邏輯（驗證憑證、生成 Token）
    7. 返回 LoginResponse

    Args:
        request: 登入請求（email, password）
        db: 資料庫 Session

    Returns:
        LoginResponse: 包含使用者資料和 access token

    Raises:
        HTTPException 401: 帳號或密碼錯誤
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
    使用 Refresh Token 刷新 Access Token

    依賴注入流程：
    1. FastAPI 驗證 RefreshTokenRequest
    2. 轉換為 RefreshTokenInputDTO
    3. 注入 AsyncSession
    4. 建立 UserRepository
    5. 建立 RefreshTokenUseCase
    6. 執行 Refresh Token 驗證和 Access Token 生成
    7. 返回 TokenResponse

    Args:
        request: 刷新 Token 請求（包含 refresh_token）
        db: 資料庫 Session

    Returns:
        TokenResponse: 包含新的 access token

    Raises:
        HTTPException 401: Refresh Token 無效或過期
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
    "/users/me",
    status_code=status.HTTP_200_OK,
    response_model=RegisterResponse
)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """
    取得當前登入使用者的資料

    需要在 HTTP Header 中提供有效的 JWT Token:
    Authorization: Bearer <access_token>

    Args:
        current_user: 當前使用者（由 get_current_user 依賴注入）

    Returns:
        RegisterResponse: 使用者資料

    Raises:
        HTTPException 401: Token 無效或過期
        HTTPException 404: 使用者不存在
    """
    return RegisterResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,  # Entity 使用 is_active
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )
