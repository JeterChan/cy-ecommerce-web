from decimal import Decimal
from pydantic import BaseModel


class DashboardStatsDTO(BaseModel):
    total_products: int
    low_stock_count: int
    today_orders: int
    today_sales: Decimal
