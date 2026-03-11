"""
Order API Routes

定義 Order 模組的 HTTP API 端點
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from infrastructure.database import get_db, get_redis
from redis.asyncio import Redis
from core.security import verify_token

from modules.order.application.dtos import CreateOrderRequest, UpdateOrderStatusRequest
from modules.order.application.dtos import OrderResponse, OrderListResponse, OrderItemResponse
from modules.order.application.use_cases.create_order import CreateOrderUseCase
from modules.order.application.use_cases.update_order import UpdateOrderStatusUseCase
from modules.order.infrastructure.repositories.postgres_order_repository import PostgresOrderRepository
from modules.order.infrastructure.repositories.redis_cart_repository import OrderCartAdapter
from modules.cart.infrastructure.repositories.redis_repository import RedisCartRepository
from modules.product.infrastructure.repository import SqlAlchemyProductRepository
from shared.exceptions import BusinessRuleViolationException, ResourceNotFoundException


router = APIRouter(prefix="/orders", tags=["Orders"])
security = HTTPBearer()


# ==================== Dependency Injection ====================

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> str:
    """
    取得當前登入使用者 ID

    Args:
        credentials: JWT Token
        db: 資料庫 Session

    Returns:
        str: 使用者 ID

    Raises:
        HTTPException: 401 未授權
    """
    token = credentials.credentials
    payload = verify_token(token)

    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無效的認證令牌"
        )

    return payload["sub"]


async def get_create_order_use_case(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> CreateOrderUseCase:
    """
    建立 CreateOrderUseCase 實例

    Args:
        db: 資料庫 Session
        redis: Redis 客戶端

    Returns:
        CreateOrderUseCase: 建立訂單用例實例
    """
    order_repo = PostgresOrderRepository(db)
    cart_repo = RedisCartRepository(redis)
    cart_adapter = OrderCartAdapter(cart_repo)
    product_repo = SqlAlchemyProductRepository(db)

    return CreateOrderUseCase(order_repo, cart_adapter, product_repo)


async def get_update_order_status_use_case(
    db: AsyncSession = Depends(get_db)
) -> UpdateOrderStatusUseCase:
    """
    建立 UpdateOrderStatusUseCase 實例

    Args:
        db: 資料庫 Session

    Returns:
        UpdateOrderStatusUseCase: 更新訂單狀態用例實例
    """
    order_repo = PostgresOrderRepository(db)
    return UpdateOrderStatusUseCase(order_repo)


# ==================== API Endpoints ====================

@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="建立訂單",
    description="從前端傳遞的商品列表建立訂單，並查詢商品價格快照。"
)
async def create_order(
    request: CreateOrderRequest,
    user_id: str = Depends(get_current_user_id),
    use_case: CreateOrderUseCase = Depends(get_create_order_use_case)
) -> OrderResponse:
    """
    建立訂單

    從前端傳遞的商品列表建立訂單，包含以下步驟：
    1. 驗證商品列表不為空
    2. 查詢商品價格（價格快照）
    3. 計算訂單總金額
    4. 建立訂單並儲存至資料庫
    5. （可選）清空購物車

    Args:
        request: 建立訂單請求（包含商品列表）
        user_id: 使用者 ID（從 JWT 取得）
        use_case: 建立訂單用例

    Returns:
        OrderResponse: 建立完成的訂單

    Raises:
        400: 商品列表為空或業務規則驗證失敗
        404: 商品不存在
        500: 伺服器錯誤
    """
    print(f"\n{'='*60}")
    print(f"📦 [Order API] 收到建立訂單請求")
    print(f"👤 [Order API] 使用者 ID: {user_id}")
    print(f"📝 [Order API] 請求內容:")
    print(f"   - 商品數量: {len(request.items)}")
    for idx, item in enumerate(request.items, 1):
        print(f"   - 商品 {idx}: ID={item.product_id}, 數量={item.quantity}")
    print(f"   - 運費: {request.shipping_fee}")
    print(f"   - 備註: {request.note or '無'}")
    print(f"{'='*60}\n")

    try:
        print(f"🔄 [Order API] 開始執行建立訂單 Use Case...")

        # 將 Pydantic 模型轉換為 Use Case 輸入
        from modules.order.application.use_cases.create_order import CreateOrderItemInput
        items_input = [
            CreateOrderItemInput(product_id=item.product_id, quantity=item.quantity)
            for item in request.items
        ]

        order = await use_case.execute(
            user_id=user_id,
            items=items_input,
            shipping_fee=request.shipping_fee,
            note=request.note
        )

        print(f"✅ [Order API] 訂單建立成功!")
        print(f"📋 [Order API] 訂單 ID: {order.id}")
        print(f"💰 [Order API] 訂單總額: {order.total_amount}")
        print(f"📦 [Order API] 商品數量: {len(order.items)}")

        # 轉換為 Response DTO
        response = OrderResponse(
            id=order.id,
            user_id=order.user_id,
            status=order.status,
            total_amount=order.total_amount,
            shipping_fee=order.shipping_fee,
            note=order.note,
            items=[
                OrderItemResponse(
                    id=item.id,
                    order_id=item.order_id or order.id,
                    product_id=item.product_id,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    subtotal=item.subtotal,
                    created_at=item.created_at,
                    updated_at=item.updated_at
                )
                for item in order.items
            ],
            created_at=order.created_at,
            updated_at=order.updated_at
        )

        print(f"✨ [Order API] 回傳訂單資料\n")
        return response

    except BusinessRuleViolationException as e:
        print(f"❌ [Order API] 業務規則驗證失敗: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ResourceNotFoundException as e:
        print(f"❌ [Order API] 資源不存在: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        print(f"❌ [Order API] 建立訂單發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"建立訂單失敗: {str(e)}"
        )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="查詢訂單詳情",
    description="根據訂單 ID 查詢訂單詳細資訊"
)
async def get_order(
    order_id: int,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> OrderResponse:
    """
    查詢訂單詳情

    Args:
        order_id: 訂單 ID
        user_id: 使用者 ID（從 JWT 取得）
        db: 資料庫 Session

    Returns:
        OrderResponse: 訂單詳情

    Raises:
        404: 訂單不存在或無權限查看
    """
    order_repo = PostgresOrderRepository(db)
    order = await order_repo.get_by_id(order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"訂單 {order_id} 不存在"
        )

    # 驗證使用者權限
    if order.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限查看此訂單"
        )

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total_amount=order.total_amount,
        shipping_fee=order.shipping_fee,
        note=order.note,
        items=[
            OrderItemResponse(
                id=item.id,
                order_id=item.order_id,
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
            for item in order.items
        ],
        created_at=order.created_at,
        updated_at=order.updated_at
    )


@router.get(
    "",
    response_model=OrderListResponse,
    summary="查詢使用者訂單列表",
    description="查詢當前使用者的所有訂單"
)
async def list_orders(
    skip: int = 0,
    limit: int = 20,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> OrderListResponse:
    """
    查詢使用者訂單列表

    Args:
        skip: 略過筆數（用於分頁）
        limit: 限制筆數（用於分頁）
        user_id: 使用者 ID（從 JWT 取得）
        db: 資料庫 Session

    Returns:
        OrderListResponse: 訂單列表
    """
    order_repo = PostgresOrderRepository(db)
    orders = await order_repo.get_by_user_id(user_id, skip=skip, limit=limit)

    return OrderListResponse(
        orders=[
            OrderResponse(
                id=order.id,
                user_id=order.user_id,
                status=order.status,
                total_amount=order.total_amount,
                shipping_fee=order.shipping_fee,
                note=order.note,
                items=[
                    OrderItemResponse(
                        id=item.id,
                        order_id=item.order_id,
                        product_id=item.product_id,
                        product_name=item.product_name,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                        subtotal=item.subtotal,
                        created_at=item.created_at,
                        updated_at=item.updated_at
                    )
                    for item in order.items
                ],
                created_at=order.created_at,
                updated_at=order.updated_at
            )
            for order in orders
        ],
        total=len(orders),
        skip=skip,
        limit=limit
    )


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="更新訂單狀態",
    description="更新指定訂單的狀態（如：PENDING → PAID → SHIPPED → COMPLETED）"
)
async def update_order_status(
    order_id: int,
    request: UpdateOrderStatusRequest,
    user_id: str = Depends(get_current_user_id),
    use_case: UpdateOrderStatusUseCase = Depends(get_update_order_status_use_case)
) -> OrderResponse:
    """
    更新訂單狀態

    業務規則：
    - PENDING 可轉換到 PAID, CANCELLED
    - PAID 可轉換到 SHIPPED, REFUNDED, CANCELLED
    - SHIPPED 可轉換到 COMPLETED, REFUNDED
    - COMPLETED 可轉換到 REFUNDED
    - CANCELLED 和 REFUNDED 是終態，不可再轉換

    Args:
        order_id: 訂單 ID
        request: 更新訂單狀態請求
        user_id: 使用者 ID（從 JWT 取得）
        use_case: 更新訂單狀態用例

    Returns:
        OrderResponse: 更新後的訂單

    Raises:
        403: 無權限修改此訂單
        404: 訂單不存在
        400: 狀態轉換不合法
    """
    try:
        order = await use_case.execute(
            order_id=order_id,
            new_status=request.status,
            user_id=user_id
        )

        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            status=order.status,
            total_amount=order.total_amount,
            shipping_fee=order.shipping_fee,
            note=order.note,
            items=[
                OrderItemResponse(
                    id=item.id,
                    order_id=item.order_id or order.id,
                    product_id=item.product_id,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    subtotal=item.subtotal,
                    created_at=item.created_at,
                    updated_at=item.updated_at
                )
                for item in order.items
            ],
            created_at=order.created_at,
            updated_at=order.updated_at
        )

    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except BusinessRuleViolationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新訂單狀態失敗: {str(e)}"
        )



