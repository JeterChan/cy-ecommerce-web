"""
Order Module - Port Interfaces

定義 Order 模組對外部模組的依賴介面（Port）。
跨模組依賴統一透過 Port 介面進行，不直接 import 其他模組的具體實作。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import List
from uuid import UUID


@dataclass
class CheckoutProduct:
    """
    結帳用商品值物件

    Order 模組對商品資訊的本地表示，
    包含結帳流程所需的所有欄位。
    """
    id: UUID
    name: str
    price: Decimal
    stock_quantity: int
    is_active: bool


class IProductPort(ABC):
    """
    商品操作 Port

    Order 模組透過此介面操作商品，用於：
    - 結帳時悲觀鎖取得商品並扣減庫存
    - 取消訂單時回補庫存
    """

    @abstractmethod
    async def get_products_for_checkout(self, product_ids: List[UUID]) -> List[CheckoutProduct]:
        """
        取得結帳用商品（含悲觀鎖 FOR UPDATE）

        按 ID 排序防止死鎖。

        Args:
            product_ids: 商品 UUID 列表

        Returns:
            CheckoutProduct 列表
        """
        pass

    @abstractmethod
    async def deduct_stock(self, product_id: UUID, quantity: int) -> None:
        """
        扣減商品庫存

        必須在 DB 事務內呼叫。

        Args:
            product_id: 商品 UUID
            quantity: 扣減數量
        """
        pass

    @abstractmethod
    async def restore_stock(self, product_id: UUID, quantity: int) -> None:
        """
        回補商品庫存（取消訂單時使用）

        使用原子操作（FOR UPDATE）確保一致性。

        Args:
            product_id: 商品 UUID
            quantity: 回補數量
        """
        pass
