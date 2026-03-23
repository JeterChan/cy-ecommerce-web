from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from typing import List, Optional
import uuid

from infrastructure.database import get_db, get_redis
from infrastructure.stock_redis_service import StockRedisService
from core.security import verify_token
from modules.auth.infrastructure.repository import UserRepository

from modules.order.application.dtos.checkout_request import CheckoutRequest
from modules.order.application.dtos.order_response import OrderResponse
from modules.order.application.dtos.order_list_response import OrderListResponse
from modules.order.application.dtos.update_status_request import UpdateStatusRequest
from modules.order.application.use_cases.checkout import CheckoutUseCase
from modules.order.application.use_cases.update_order_status import UpdateOrderStatusUseCase
from modules.order.infrastructure.repositories.postgres_order_repository import PostgresOrderRepository
from modules.cart.infrastructure.repositories.hybrid_repository import HybridCartRepository
from modules.product.infrastructure.repository import SqlAlchemyProductRepository
from modules.order.domain.exceptions import (
    InsufficientStockException,
    PriceChangedException,
    EmptyCartException
)

router = APIRouter(prefix="/orders", tags=["Orders"])
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials
    payload = verify_token(token, token_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email = payload.get("sub")
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post(
    "/checkout",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="執行結帳",
    description="從目前的購物車建立訂單，並扣除庫存 (原子操作)"
)
async def checkout(
    request: CheckoutRequest,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    order_repo = PostgresOrderRepository(db)
    cart_repo = HybridCartRepository(redis, db)
    product_repo = SqlAlchemyProductRepository(db)
    stock_service = StockRedisService(redis, db)

    use_case = CheckoutUseCase(db, order_repo, cart_repo, product_repo, stock_service)
    
    try:
        return await use_case.execute(user_id=user.id, request=request)
    except (InsufficientStockException, PriceChangedException, EmptyCartException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during checkout: {str(e)}"
        )

@router.get(
    "",
    response_model=OrderListResponse,
    summary="取得訂單列表",
    description="取得當前使用者的所有訂單歷史"
)
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    order_repo = PostgresOrderRepository(db)
    user_uuid = user.id if isinstance(user.id, uuid.UUID) else uuid.UUID(str(user.id))
    
    orders = await order_repo.get_by_user_id(user_id=user_uuid, skip=skip, limit=limit)
    total = await order_repo.count_by_user_id(user_id=user_uuid)
    
    response_list = [OrderResponse.model_validate(order) for order in orders]
        
    return OrderListResponse(
        orders=response_list,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="取得訂單詳情",
    description="根據訂單 ID 取得詳細資訊，包含所有購買項目"
)
async def get_order_detail(
    order_id: uuid.UUID,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    order_repo = PostgresOrderRepository(db)
    
    order = await order_repo.get_by_id(order_id=order_id)
    
    user_uuid = user.id if isinstance(user.id, uuid.UUID) else uuid.UUID(str(user.id))
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
        
    if order.user_id != user_uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )
    
    return OrderResponse.model_validate(order)

@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="更新訂單狀態",
    description="更新指定訂單的狀態（例如：取消訂單）"
)
async def update_order_status(
    order_id: uuid.UUID,
    request: UpdateStatusRequest,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    order_repo = PostgresOrderRepository(db)
    product_repo = SqlAlchemyProductRepository(db)
    
    use_case = UpdateOrderStatusUseCase(db, order_repo, product_repo)
    
    try:
        user_uuid = user.id if isinstance(user.id, uuid.UUID) else uuid.UUID(str(user.id))
        order = await use_case.execute(
            order_id=order_id,
            user_id=user_uuid,
            new_status=request.status
        )
        return OrderResponse.model_validate(order)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating order status: {str(e)}"
        )
