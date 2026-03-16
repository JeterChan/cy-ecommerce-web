from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from modules.product.domain.entities import Product

class ProductRepository(ABC):
    @abstractmethod
    def create(self, product: Product) -> Product:
        pass

    @abstractmethod
    def get_by_id(self, product_id: UUID) -> Optional[Product]:
        pass

    @abstractmethod
    def list(self, skip: int = 0, limit: int = 100) -> List[Product]:
        pass

    @abstractmethod
    def update(self, product: Product) -> Product:
        pass

    @abstractmethod
    def delete(self, product_id: UUID) -> bool:
        pass