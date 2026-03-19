"""
Admin Dashboard API Routes

提供管理後台統計數據的 HTTP API 端點
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import get_db
from modules.auth.presentation.routes import require_admin
from modules.auth.domain.entities import UserEntity
from modules.product.application.use_cases.get_dashboard_stats import GetDashboardStatsUseCase
from modules.product.application.dtos.dashboard_stats_dto import DashboardStatsDTO

router = APIRouter(prefix="/admin/dashboard", tags=["Admin Dashboard"])


@router.get(
    "/stats",
    response_model=DashboardStatsDTO,
    summary="取得 Dashboard 統計數據 (管理員)"
)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    admin: UserEntity = Depends(require_admin)
) -> DashboardStatsDTO:
    """取得商品總數、低庫存警示、今日訂單數及今日銷售額，僅限管理員"""
    from modules.product.infrastructure.repository import SqlAlchemyProductRepository
    from modules.order.infrastructure.repositories.postgres_order_repository import PostgresOrderRepository

    use_case = GetDashboardStatsUseCase(
        product_repo=SqlAlchemyProductRepository(db),
        order_repo=PostgresOrderRepository(db),
    )
    return await use_case.execute()
