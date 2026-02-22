"""
Order Module - Repository Interfaces

此檔案定義訂單 Repository 的抽象介面。
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from modules.order.domain.entities import Order


class IOrderRepository(ABC):
    """訂單 Repository 抽象介面"""

    @abstractmethod
    async def create(self, order: Order) -> Order:
        """
        建立新訂單

        Args:
            order: 訂單實體

        Returns:
            Order: 建立完成的訂單（包含生成的 ID）
        """
        pass

    @abstractmethod
    async def get_by_id(self, order_id: int) -> Optional[Order]:
        """
        根據 ID 查詢訂單

        Args:
            order_id: 訂單 ID

        Returns:
            Optional[Order]: 訂單實體，若不存在則回傳 None
        """
        pass

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """
        查詢特定使用者的所有訂單

        Args:
            user_id: 使用者 ID
            skip: 略過筆數（用於分頁）
            limit: 限制筆數（用於分頁）

        Returns:
            List[Order]: 訂單列表
        """
        pass

    @abstractmethod
    async def update(self, order: Order) -> Order:
        """
        更新訂單

        Args:
            order: 訂單實體

        Returns:
            Order: 更新後的訂單
        """
        pass

    @abstractmethod
    async def delete(self, order_id: int) -> bool:
        """
        刪除訂單

        Args:
            order_id: 訂單 ID

        Returns:
            bool: 是否成功刪除
        """
        pass

