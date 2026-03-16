from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID
from modules.product.domain.entities import Product


class IProductRepository(ABC):
    @abstractmethod
    async def create(self, product: Product) -> Product:
        pass

    @abstractmethod
    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        pass

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        category_ids: Optional[List[int]] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Product], int]:
        pass


    @abstractmethod
    async def list_admin(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        sort: str = "created_desc",
    ) -> Tuple[List[Product], int]:
        pass

    @abstractmethod
    async def update(self, product: Product) -> Product:
        pass

    @abstractmethod
    async def delete(self, product_id: UUID) -> bool:
        pass

    @abstractmethod
    async def get_by_ids_with_lock(self, product_ids: List[UUID]) -> List[Product]:
        """
        批量取得商品並加上 FOR UPDATE 鎖定。
        用於結帳等需要保證庫存一致性的場景。
        """
        pass