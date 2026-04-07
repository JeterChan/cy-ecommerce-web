from datetime import date
from typing import List, Tuple, Optional
from modules.order.domain.repository import IOrderRepository
from modules.order.domain.entities import Order


class AdminListOrdersUseCase:
    def __init__(self, order_repo: IOrderRepository):
        self.order_repo = order_repo

    async def execute(
        self,
        page: int = 1,
        limit: int = 10,
        status: Optional[str] = None,
        search_order_number: Optional[str] = None,
        search_recipient_name: Optional[str] = None,
        search_phone: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> Tuple[List[Order], int]:
        skip = (page - 1) * limit
        filters = dict(
            status=status,
            search_order_number=search_order_number,
            search_recipient_name=search_recipient_name,
            search_phone=search_phone,
            date_from=date_from,
            date_to=date_to,
        )
        orders = await self.order_repo.list_all(skip=skip, limit=limit, **filters)
        total = await self.order_repo.count_all(**filters)
        return orders, total
