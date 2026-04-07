from modules.product.domain.repository import IProductRepository
from modules.order.domain.repository import IOrderRepository
from modules.product.application.dtos.dashboard_stats_dto import DashboardStatsDTO


class GetDashboardStatsUseCase:
    """取得 admin dashboard 四項統計數據"""

    def __init__(self, product_repo: IProductRepository, order_repo: IOrderRepository):
        self.product_repo = product_repo
        self.order_repo = order_repo

    async def execute(self) -> DashboardStatsDTO:
        total_products = await self.product_repo.count_total_active()
        low_stock_count = await self.product_repo.count_low_stock()
        today_stats = await self.order_repo.get_today_stats()

        return DashboardStatsDTO(
            total_products=total_products,
            low_stock_count=low_stock_count,
            today_orders=today_stats["count"],
            today_sales=today_stats["total_sales"],
        )
