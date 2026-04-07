"""
Admin Order API Routes

定義管理員專用的訂單管理 HTTP API 端點
"""

from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
import math

from infrastructure.database import get_db
from modules.auth.presentation.routes import require_admin
from modules.auth.domain.entities import UserEntity

from modules.order.application.dtos.admin_order_response import (
    AdminOrderResponse,
    AdminOrderListResponse,
)
from modules.order.application.dtos.admin_update_order_request import (
    AdminUpdateOrderRequest,
)
from modules.order.application.use_cases.admin_list_orders import AdminListOrdersUseCase
from modules.order.application.use_cases.admin_update_order import (
    AdminUpdateOrderUseCase,
)
from modules.order.infrastructure.repositories.postgres_order_repository import (
    PostgresOrderRepository,
)
from modules.order.infrastructure.adapters import OrderProductAdapter

router = APIRouter(prefix="/admin/orders", tags=["Admin Orders"])


@router.get(
    "",
    response_model=AdminOrderListResponse,
    summary="獲取訂單列表 (管理員，支援篩選/分頁)",
)
async def admin_list_orders(
    page: int = Query(default=1, ge=1, description="頁碼"),
    limit: int = Query(default=10, ge=1, le=100, description="每頁筆數"),
    status: Optional[str] = Query(default=None, description="訂單狀態篩選"),
    search_order_number: Optional[str] = Query(
        default=None, description="訂單編號搜尋（模糊）"
    ),
    search_recipient_name: Optional[str] = Query(
        default=None, description="收件人姓名搜尋（模糊）"
    ),
    search_phone: Optional[str] = Query(
        default=None, description="收件人電話搜尋（模糊）"
    ),
    date_from: Optional[date] = Query(default=None, description="建立日期起（含）"),
    date_to: Optional[date] = Query(default=None, description="建立日期迄（含當日）"),
    db: AsyncSession = Depends(get_db),
    admin: UserEntity = Depends(require_admin),
) -> AdminOrderListResponse:
    """獲取系統中所有訂單，支援多欄位搜尋、狀態篩選與分頁"""
    order_repo = PostgresOrderRepository(db)
    use_case = AdminListOrdersUseCase(order_repo)

    orders, total = await use_case.execute(
        page=page,
        limit=limit,
        status=status,
        search_order_number=search_order_number or None,
        search_recipient_name=search_recipient_name or None,
        search_phone=search_phone or None,
        date_from=date_from,
        date_to=date_to,
    )

    pages = math.ceil(total / limit) if total > 0 else 1

    return AdminOrderListResponse(
        orders=[AdminOrderResponse.model_validate(o) for o in orders],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get(
    "/{order_id}", response_model=AdminOrderResponse, summary="獲取訂單詳情 (管理員)"
)
async def admin_get_order_detail(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: UserEntity = Depends(require_admin),
) -> AdminOrderResponse:
    """獲取特定訂單的詳細資訊，包含管理員備註"""
    order_repo = PostgresOrderRepository(db)
    order = await order_repo.get_by_id(order_id)

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="訂單不存在")

    return AdminOrderResponse.model_validate(order)


@router.patch(
    "/{order_id}", response_model=AdminOrderResponse, summary="更新訂單 (管理員)"
)
async def admin_update_order(
    order_id: UUID,
    request: AdminUpdateOrderRequest,
    db: AsyncSession = Depends(get_db),
    admin: UserEntity = Depends(require_admin),
) -> AdminOrderResponse:
    """更新訂單狀態或管理員備註"""
    order_repo = PostgresOrderRepository(db)
    product_port = OrderProductAdapter(db)

    use_case = AdminUpdateOrderUseCase(db, order_repo, product_port)

    try:
        updated_order = await use_case.execute(
            order_id=order_id, new_status=request.status, admin_note=request.admin_note
        )
        return AdminOrderResponse.model_validate(updated_order)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新訂單時發生錯誤: {str(e)}",
        )
