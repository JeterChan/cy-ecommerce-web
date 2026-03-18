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
        status: Optional[str] = None
    ) -> Tuple[List[Order], int]:
        skip = (page - 1) * limit
        orders = await self.order_repo.list_all(skip=skip, limit=limit, status=status)
        total = await self.order_repo.count_all(status=status)
        return orders, total
