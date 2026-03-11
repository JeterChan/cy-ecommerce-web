from abc import ABC, abstractmethod
from typing import List, Optional
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
    async def list(self, skip: int = 0, limit: int = 100) -> List[Product]:
        pass

    @abstractmethod
    async def update(self, product: Product) -> Product:
        pass

    @abstractmethod
    async def delete(self, product_id: UUID) -> bool:
        pass