"""
Order Module - Repository Interfaces

此檔案定義訂單 Repository 的抽象介面。
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional
from uuid import UUID
from modules.order.domain.entities import Order


class IOrderRepository(ABC):
    """訂單 Repository 抽象介面"""

    @abstractmethod
    async def create(self, order: Order) -> Order:
        """建立新訂單"""
        pass

    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> Optional[Order]:
        """根據 ID 查詢訂單"""
        pass

    @abstractmethod
    async def get_by_user_id(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """查詢特定使用者的所有訂單"""
        pass

    @abstractmethod
    async def count_by_user_id(self, user_id: UUID) -> int:
        """計算特定使用者的訂單總數"""
        pass

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        search_order_number: Optional[str] = None,
        search_recipient_name: Optional[str] = None,
        search_phone: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> List[Order]:
        """查詢所有訂單 (管理員用)"""
        pass

    @abstractmethod
    async def count_all(
        self,
        status: Optional[str] = None,
        search_order_number: Optional[str] = None,
        search_recipient_name: Optional[str] = None,
        search_phone: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> int:
        """計算所有訂單總數 (管理員用)"""
        pass

    @abstractmethod
    async def update(self, order: Order) -> Order:
        """更新訂單"""
        pass

    @abstractmethod
    async def delete(self, order_id: UUID) -> bool:
        """刪除訂單"""
        pass

    @abstractmethod
    async def get_today_stats(self) -> dict:
        """取得台灣時區今日訂單數及銷售額（排除 CANCELLED、REFUNDED）"""
        pass


class ICartAdapter(ABC):
    """購物車適配器抽象介面"""

    @abstractmethod
    async def get_cart_items(self, owner_id: str):
        pass

    @abstractmethod
    async def clear_cart(self, owner_id: str) -> None:
        pass

    @abstractmethod
    async def is_cart_empty(self, owner_id: str) -> bool:
        pass
