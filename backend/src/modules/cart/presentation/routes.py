"""
Cart API Routes

定義 Cart 模組的 HTTP API 端點
支援訪客購物車 (Guest Cart) 與會員購物車 (Member Cart)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Tuple
import uuid

from infrastructure.database import get_redis, get_db
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from modules.cart.infrastructure.repositories.redis_repository import RedisCartRepository
from modules.cart.infrastructure.repositories.sql_repository import SQLCartRepository
from modules.cart.domain.repository import ICartRepository
from modules.cart.application.use_cases import (
    AddToCartUseCase,
    UpdateCartItemQuantityUseCase,
    RemoveFromCartUseCase,
    ClearCartUseCase,
    GetCartUseCase,
    GetCartItemUseCase,
    GetCartSummaryUseCase,
)
from modules.cart.domain.entities import CartItemResponse, CartItemCreate, CartItemUpdate
from modules.cart.infrastructure.utils import (
    generate_guest_token,
    set_guest_token_cookie,
    get_guest_token_from_cookie,
    validate_guest_token
)
from core.security import verify_token
from modules.auth.infrastructure.repository import UserRepository


router = APIRouter(prefix="/cart", tags=["Cart"])
security = HTTPBearer(auto_error=False)  # auto_error=False 使其成為可選


# ==================== Dependency Injection ====================

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    取得當前使用者（可選）

    若有有效的 JWT Token，回傳使用者實體
    若無 Token 或 Token 無效，回傳 None（不拋出錯誤）

    Returns:
        Optional[UserEntity]: 使用者實體或 None
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = verify_token(token, token_type="access")

        if not payload:
            return None

        # Token 的 sub 欄位是 email（與 auth 模組一致）
        email = payload.get("sub")
        if not email:
            return None

        # 查詢使用者
        user_repo = UserRepository(db)
        user = await user_repo.get_by_email(email)

        return user
    except Exception:
        # Token 解析失敗或其他錯誤，視為訪客
        return None


async def get_cart_repository(
    request: Request,
    response: Response,
    redis: Redis = Depends(get_redis),
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user_optional)
) -> Tuple[ICartRepository, str]:
    """
    根據使用者狀態選擇 Repository

    邏輯:
    - 若有登入（user 不為 None）→ 使用 SQLCartRepository，owner_id = str(user.id)
    - 若未登入（user 為 None）→ 使用 RedisCartRepository，owner_id = guest_token

    Returns:
        Tuple[ICartRepository, str]: (repository, owner_id)
    """
    if user:
        # 會員：使用 SQL Repository
        repository = SQLCartRepository(db)
        owner_id = str(user.id)
    else:
        # 訪客：使用 Redis Repository + Guest Token
        token = get_guest_token_from_cookie(request)

        if token and validate_guest_token(token):
            owner_id = token
        else:
            # 生成新 Token 並設定 Cookie
            owner_id = generate_guest_token()
            set_guest_token_cookie(response, owner_id)

        repository = RedisCartRepository(redis)

    return repository, owner_id


# ==================== API Endpoints ====================

@router.post(
    "/items",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="新增商品到購物車",
    description="將商品加入購物車，若商品已存在則累加數量（支援訪客與會員）"
)
async def add_to_cart(
    item: CartItemCreate,
    repo_and_id: Tuple[ICartRepository, str] = Depends(get_cart_repository)
) -> CartItemResponse:
    """
    新增商品到購物車

    - **product_id**: 商品 UUID (必填)
    - **quantity**: 數量 (必填，大於 0)

    行為:
    - 若商品已存在，則累加數量
    - 若商品不存在，則新增項目
    - 自動識別訪客/會員（透過 Authorization header 或 Cookie）
    - 訪客：儲存在 Redis
    - 會員：儲存在 PostgreSQL
    """
    repository, owner_id = repo_and_id

    try:
        use_case = AddToCartUseCase(repository)
        result = await use_case.execute(
            owner_id=owner_id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=List[CartItemResponse],
    summary="取得購物車",
    description="取得購物車所有商品（支援訪客與會員）"
)
async def get_cart(
    repo_and_id: Tuple[ICartRepository, str] = Depends(get_cart_repository)
) -> List[CartItemResponse]:
    """
    取得購物車所有商品

    返回:
    - 購物車項目列表 (可能為空)
    """
    repository, owner_id = repo_and_id
    use_case = GetCartUseCase(repository)
    items = await use_case.execute(owner_id=owner_id)
    return items


@router.get(
    "/items/{product_id}",
    response_model=CartItemResponse,
    summary="查詢購物車中的單一商品",
    description="根據商品 ID 查詢購物車中的項目"
)
async def get_cart_item(
    product_id: uuid.UUID,
    repo_and_id: Tuple[ICartRepository, str] = Depends(get_cart_repository)
) -> CartItemResponse:
    """
    查詢購物車中的單一商品

    - **product_id**: 商品 UUID
    """
    repository, owner_id = repo_and_id
    use_case = GetCartItemUseCase(repository)
    item = await use_case.execute(
        owner_id=owner_id,
        product_id=product_id
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found in cart"
        )

    return item


@router.put(
    "/items/{product_id}",
    response_model=CartItemResponse,
    summary="更新商品數量",
    description="更新購物車中指定商品的數量"
)
async def update_cart_item(
    product_id: uuid.UUID,
    item_update: CartItemUpdate,
    repo_and_id: Tuple[ICartRepository, str] = Depends(get_cart_repository)
) -> CartItemResponse:
    """
    更新購物車商品數量

    - **product_id**: 商品 UUID
    - **quantity**: 新數量 (必填，大於 0)
    """
    repository, owner_id = repo_and_id

    try:
        use_case = UpdateCartItemQuantityUseCase(repository)
        result = await use_case.execute(
            owner_id=owner_id,
            product_id=product_id,
            quantity=item_update.quantity
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/items/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="移除商品",
    description="從購物車移除指定商品"
)
async def remove_cart_item(
    product_id: uuid.UUID,
    repo_and_id: Tuple[ICartRepository, str] = Depends(get_cart_repository)
) -> None:
    """
    從購物車移除商品

    - **product_id**: 商品 UUID
    """
    repository, owner_id = repo_and_id
    use_case = RemoveFromCartUseCase(repository)
    await use_case.execute(
        owner_id=owner_id,
        product_id=product_id
    )


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="清空購物車",
    description="清空購物車所有商品"
)
async def clear_cart(
    repo_and_id: Tuple[ICartRepository, str] = Depends(get_cart_repository)
) -> None:
    """
    清空購物車所有商品
    """
    repository, owner_id = repo_and_id
    use_case = ClearCartUseCase(repository)
    await use_case.execute(owner_id=owner_id)


@router.get(
    "/summary",
    summary="取得購物車摘要",
    description="取得購物車商品總數量和商品種類數"
)
async def get_cart_summary(
    repo_and_id: Tuple[ICartRepository, str] = Depends(get_cart_repository)
):
    """
    取得購物車摘要

    返回:
    - total_quantity: 商品總數量
    - total_items: 商品種類數

    注意:
    - 購物車不儲存價格，總金額需前端動態查詢 Product 計算
    """
    repository, owner_id = repo_and_id
    use_case = GetCartSummaryUseCase(repository)
    return await use_case.execute(owner_id=owner_id)

