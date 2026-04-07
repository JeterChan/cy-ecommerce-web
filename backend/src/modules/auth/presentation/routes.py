"""
Auth API Routes

定義 Auth 模組的 HTTP API 端點
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from infrastructure.database import get_db, get_redis
from infrastructure.redis.token_manager import RedisTokenManager
from core.security import verify_token
from core.exceptions import (
    InvalidCredentialsError,
    EmailNotVerifiedError,
    DuplicateEmailError,
    UserNotRegisteredError,
    UserNotFoundError,
)

from modules.auth.application.use_cases import (
    RegisterUserUseCase,
    LoginUserUseCase,
    RefreshTokenUseCase,
    GetProfileUseCase,
    UpdateProfileUseCase,
    RequestEmailChangeUseCase,
    VerifyEmailChangeUseCase,
    VerifyEmailUseCase,
    ForgotPasswordUseCase,
    ResetPasswordUseCase,
    ChangePasswordUseCase,
)
from modules.auth.application.dtos import (
    RegisterRequestDTO,
    LoginRequestDTO,
    RefreshTokenRequestDTO,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    DeleteAccountRequest,
    UserResponseDTO,
    LoginResponseDTO,
    TokenResponseDTO,
    UserProfileResponse,
    UpdateProfileResponse,
    UpdateProfileRequest,
    EmailChangeRequest,
    VerifyEmailChangeRequest,
    EmailVerifyType,
)
from modules.auth.infrastructure.repository import UserRepository
from modules.auth.infrastructure.password_hasher import BcryptPasswordHasher
from modules.auth.domain.entities import UserEntity

from modules.auth.infrastructure.adapters import CartMergeAdapter

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
security = HTTPBearer()


# ==================== Dependency Functions ====================


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> UserEntity:
    token = credentials.credentials
    payload = verify_token(token, token_type="access")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無效或過期的 Token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 缺少使用者資訊",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="使用者不存在或已被刪除"
        )

    # 強制檢查信箱驗證狀態
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="請先完成信箱驗證"
        )

    return user


async def require_admin(
    current_user: UserEntity = Depends(get_current_user),
) -> UserEntity:
    """驗證當前使用者是否為管理員"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="權限不足，僅限管理員操作"
        )
    return current_user


# ==================== API Endpoints ====================


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseDTO,
    summary="註冊新使用者",
    description="建立新的使用者帳號並發送驗證信",
)
async def register_user(
    data: RegisterRequestDTO,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> UserResponseDTO:
    try:
        user_repo = UserRepository(db)
        token_manager = RedisTokenManager(redis)
        use_case = RegisterUserUseCase(user_repo, token_manager)
        user_dto = await use_case.execute(data)
        return user_dto
    except DuplicateEmailError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get(
    "/email-verify",
    status_code=status.HTTP_200_OK,
    summary="驗證註冊信箱",
    description="透過信件中的 Token 驗證並啟用帳號",
)
async def verify_user_email(
    token: str, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)
) -> dict:
    try:
        user_repo = UserRepository(db)
        token_manager = RedisTokenManager(redis)
        use_case = VerifyEmailUseCase(user_repo, token_manager)
        await use_case.execute(token)
        return {"message": "信箱驗證成功，帳號已啟用"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/forgot-password",
    status_code=status.HTTP_202_ACCEPTED,
    summary="請求重設密碼",
    description="向指定的 Email 發送密碼重設連結",
)
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    try:
        user_repo = UserRepository(db)
        token_manager = RedisTokenManager(redis)
        use_case = ForgotPasswordUseCase(user_repo, token_manager)
        await use_case.execute(data.email)
        return {"message": "重設郵件已發送，請檢查您的信箱"}
    except UserNotRegisteredError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="重設密碼",
    description="透過 Token 設定新密碼",
)
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    try:
        user_repo = UserRepository(db)
        token_manager = RedisTokenManager(redis)
        use_case = ResetPasswordUseCase(user_repo, token_manager)
        await use_case.execute(data.token, data.new_password)
        return {"message": "密碼已成功重設"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/me/change-password",
    status_code=status.HTTP_200_OK,
    summary="變更密碼",
    description="登入狀態下變更目前密碼",
)
async def change_password(
    data: ChangePasswordRequest,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        user_repo = UserRepository(db)
        use_case = ChangePasswordUseCase(user_repo, BcryptPasswordHasher())
        await use_case.execute(current_user.id, data.old_password, data.new_password)
        return {"message": "密碼已成功變更"}
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponseDTO,
    summary="使用者登入",
    description="使用 Email 和密碼登入",
)
async def login_user(
    data: LoginRequestDTO,
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> LoginResponseDTO:
    try:
        user_repo = UserRepository(db)
        use_case = LoginUserUseCase(user_repo, BcryptPasswordHasher())
        login_dto = await use_case.execute(data)

        # 購物車合併邏輯（透過 Adapter 封裝，失敗不影響登入）
        cart_merge_port = CartMergeAdapter(db, redis)
        await cart_merge_port.merge_guest_cart(request, login_dto.user.id)

        return login_dto

    except UserNotRegisteredError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except EmailNotVerifiedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except InvalidCredentialsError as e:
        # InvalidCredentialsError 在 Use Case 中可能包含 "請先完成信箱驗證"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponseDTO,
    summary="刷新 Access Token",
)
async def refresh_token(
    data: RefreshTokenRequestDTO, db: AsyncSession = Depends(get_db)
) -> TokenResponseDTO:
    try:
        user_repo = UserRepository(db)
        use_case = RefreshTokenUseCase(user_repo)
        return await use_case.execute(data)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponseDTO,
    summary="取得當前使用者資訊",
)
async def get_me(
    current_user: UserEntity = Depends(get_current_user),
) -> UserResponseDTO:
    return UserResponseDTO(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.get(
    "/me/profile",
    status_code=status.HTTP_200_OK,
    response_model=UserProfileResponse,
    summary="取得使用者個人檔案",
)
async def get_my_profile(
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfileResponse:
    try:
        user_repo = UserRepository(db)
        use_case = GetProfileUseCase(user_repo)
        return await use_case.execute(current_user.id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch(
    "/me/profile",
    status_code=status.HTTP_200_OK,
    response_model=UpdateProfileResponse,
    summary="更新使用者個人檔案",
)
async def update_my_profile(
    data: UpdateProfileRequest,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UpdateProfileResponse:
    from core.exceptions import ValidationError as DomainValidationError

    try:
        user_repo = UserRepository(db)
        use_case = UpdateProfileUseCase(user_repo)
        return await use_case.execute(current_user.id, data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DomainValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )


@router.post(
    "/me/email/change", status_code=status.HTTP_202_ACCEPTED, summary="請求變更電子郵件"
)
async def request_email_change(
    data: EmailChangeRequest,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    from infrastructure.redis.token_manager import RedisTokenManager
    from core.exceptions import ValidationError as DomainValidationError

    try:
        user_repo = UserRepository(db)
        token_manager = RedisTokenManager(redis)
        use_case = RequestEmailChangeUseCase(
            user_repo, token_manager, BcryptPasswordHasher()
        )
        await use_case.execute(current_user.id, data)
        return {"message": "驗證信已發送至新舊 Email，請分別點擊連結完成驗證"}
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DomainValidationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get(
    "/me/email/verify", status_code=status.HTTP_200_OK, summary="驗證 Email 變更"
)
async def verify_email_change(
    token: str,
    type: EmailVerifyType,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    from infrastructure.redis.token_manager import RedisTokenManager
    from core.exceptions import ValidationError as DomainValidationError

    try:
        user_repo = UserRepository(db)
        token_manager = RedisTokenManager(redis)
        use_case = VerifyEmailChangeUseCase(user_repo, token_manager)
        request = VerifyEmailChangeRequest(token=token, type=type)
        return await use_case.execute(user_id, request)
    except DomainValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/me", status_code=status.HTTP_200_OK, summary="刪除帳戶")
async def delete_account(
    data: DeleteAccountRequest,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from modules.auth.application.use_cases.delete_account import DeleteAccountUseCase

    try:
        user_repo = UserRepository(db)
        use_case = DeleteAccountUseCase(user_repo, BcryptPasswordHasher())
        await use_case.execute(current_user.id, data.password)
        return {"message": "帳戶已成功軟刪除，您的 Email 已釋出"}
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
