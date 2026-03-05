"""
Auth API Routes

定義 Auth 模組的 HTTP API 端點
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from infrastructure.database import get_db, get_redis
from core.security import verify_token
from core.exceptions import InvalidCredentialsError, DuplicateEmailError, UserNotRegisteredError, UserNotFoundError

from modules.auth.application.use_cases import (
    RegisterUserUseCase,
    LoginUserUseCase,
    RefreshTokenUseCase,
)
from modules.auth.application.use_cases.get_profile import GetProfileUseCase
from modules.auth.application.use_cases.update_profile import UpdateProfileUseCase
from modules.auth.application.use_cases.request_email_change import RequestEmailChangeUseCase
from modules.auth.application.use_cases.verify_email_change import VerifyEmailChangeUseCase
from modules.auth.application.dtos import (
    RegisterRequestDTO,
    LoginRequestDTO,
    RefreshTokenRequestDTO,
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
from modules.auth.infrastructure.repositories.user_repository import UserRepository
from modules.auth.domain.entities.UserEntity import UserEntity

from modules.cart.application.services import CartMergeService
from modules.cart.domain.utils import get_guest_token_from_cookie


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
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> LoginResponseDTO:
    """
    使用者登入

    - **email**: 使用者信箱
    - **password**: 密碼
    - **remember_me**: 是否記住我（會生成 Refresh Token）

    登入流程：
    1. 驗證使用者帳號密碼
    2. 生成 JWT Tokens
    3. 自動合併訪客購物車（若有）
    """
    try:
        # 1. 建立 Repository 和 Use Case
        user_repo = UserRepository(db)
        use_case = LoginUserUseCase(user_repo)

        # 2. 執行登入 Use Case
        login_dto = await use_case.execute(data)

        # 3. 購物車合併（訪客 → 會員）
        try:
            # 取得訪客 Token（從 Cookie）
            guest_token = get_guest_token_from_cookie(request)

            if guest_token:
                # 執行合併
                merge_service = CartMergeService(db, redis)
                merge_result = await merge_service.merge_guest_to_member(
                    guest_token=guest_token,
                    user_id=login_dto.user.id
                )

                # 記錄合併結果（可選：加入 response 或 log）
                if merge_result["success"] and merge_result["merged_items"] > 0:
                    # 成功合併，可以記錄或通知使用者
                    pass
        except Exception as e:
            # 購物車合併失敗不應影響登入
            # 只記錄錯誤，不中斷登入流程
            print(f"Cart merge failed: {str(e)}")

        return login_dto

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


@router.get(
    "/me/profile",
    status_code=status.HTTP_200_OK,
    response_model=UserProfileResponse,
    summary="取得使用者個人檔案",
    description="取得當前登入使用者的完整個人檔案資訊"
)
async def get_my_profile(
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserProfileResponse:
    """
    取得使用者個人檔案

    需要在 Header 中提供有效的 JWT Token：
    Authorization: Bearer <access_token>

    回傳包含個人資料欄位（phone、address、carrier 等）的完整個人檔案。
    """
    try:
        user_repo = UserRepository(db)
        use_case = GetProfileUseCase(user_repo)
        return await use_case.execute(current_user.id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch(
    "/me/profile",
    status_code=status.HTTP_200_OK,
    response_model=UpdateProfileResponse,
    summary="更新使用者個人檔案",
    description="更新當前登入使用者的可編輯個人資料欄位（部分更新）"
)
async def update_my_profile(
    data: UpdateProfileRequest,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UpdateProfileResponse:
    """
    更新使用者個人檔案（Partial Update）

    只更新請求中有提供的欄位。
    需要在 Header 中提供有效的 JWT Token：
    Authorization: Bearer <access_token>
    """
    from core.exceptions import ValidationError as DomainValidationError
    try:
        user_repo = UserRepository(db)
        use_case = UpdateProfileUseCase(user_repo)
        return await use_case.execute(current_user.id, data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DomainValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.post(
    "/me/email/change",
    status_code=status.HTTP_202_ACCEPTED,
    summary="請求變更電子郵件",
    description="驗證目前密碼後，向新舊 Email 各發送驗證連結"
)
async def request_email_change(
    data: EmailChangeRequest,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """
    請求變更電子郵件

    1. 驗證目前密碼
    2. 確認新 Email 未被佔用
    3. 發送驗證信至新舊 Email

    需要在 Header 中提供有效的 JWT Token。
    """
    from infrastructure.redis.token_manager import RedisTokenManager
    from core.exceptions import ValidationError as DomainValidationError

    try:
        user_repo = UserRepository(db)
        token_manager = RedisTokenManager(redis)
        use_case = RequestEmailChangeUseCase(user_repo, token_manager)
        await use_case.execute(current_user.id, data)
        return {"message": "驗證信已發送至新舊 Email，請分別點擊連結完成驗證"}
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except DomainValidationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get(
    "/me/email/verify",
    status_code=status.HTTP_200_OK,
    summary="驗證 Email 變更",
    description="使用驗證連結中的 token 確認 Email 變更"
)
async def verify_email_change(
    token: str,
    type: EmailVerifyType,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """
    驗證 Email 變更

    Query Parameters:
    - **token**: 驗證 Token（來自信件連結）
    - **type**: 驗證類型（`old` 或 `new`）
    - **user_id**: 使用者 ID

    新舊兩端均驗證完成後，Email 才會正式更新。
    """
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


@router.delete(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="刪除帳戶",
    description="將帳戶標記為停用（軟刪除），30 天後系統將自動永久刪除資料"
)
async def delete_account(
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    刪除帳戶（軟刪除）

    - 帳戶立即停用，目前 Token 之後的請求將被拒絕
    - 30 天後系統定期任務將永久刪除帳戶資料

    需要在 Header 中提供有效的 JWT Token。
    """
    from modules.auth.application.use_cases.delete_account import DeleteAccountUseCase

    try:
        user_repo = UserRepository(db)
        use_case = DeleteAccountUseCase(user_repo)
        await use_case.execute(current_user.id)
        return {"message": "帳戶已成功停用，將於 30 天後永久刪除"}
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


