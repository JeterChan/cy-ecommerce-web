"""
Cart Module - Port Interfaces

定義 Cart 模組對外部模組的依賴介面（Port）。
跨模組依賴統一透過 Port 介面進行，不直接 import 其他模組的具體實作。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, List
from uuid import UUID


@dataclass
class ProductSnapshot:
    """
    商品快照值物件

    Cart 模組對商品資訊的本地表示，避免直接依賴 Product 模組的 Entity。
    """

    id: UUID
    name: str
    price: Decimal
    stock_quantity: int
    is_active: bool = True
    image_url: Optional[str] = None


class IProductInfoPort(ABC):
    """
    商品資訊查詢 Port

    Cart 模組透過此介面查詢商品資訊，用於：
    - 庫存校驗（AddToCart / UpdateQuantity）
    - 商品資訊富化（顯示名稱、價格、圖片）
    """

    @abstractmethod
    async def get_product_info(self, product_id: UUID) -> Optional[ProductSnapshot]:
        """
        查詢單一商品資訊

        Args:
            product_id: 商品 UUID

        Returns:
            ProductSnapshot 或 None（商品不存在時）
        """
        pass

    @abstractmethod
    async def get_products_info(self, product_ids: List[UUID]) -> List[ProductSnapshot]:
        """
        批量查詢商品資訊

        Args:
            product_ids: 商品 UUID 列表

        Returns:
            ProductSnapshot 列表（僅包含存在的商品）
        """
        pass
