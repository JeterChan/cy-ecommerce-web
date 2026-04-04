"""
Auth Module - Port Interfaces

定義 Auth 模組對外部模組的依賴介面（Port）。
"""

from abc import ABC, abstractmethod
from uuid import UUID
from fastapi import Request


class ICartMergePort(ABC):
    """
    購物車合併 Port

    Auth 模組透過此介面在登入時合併訪客購物車到會員購物車。
    """

    @abstractmethod
    async def merge_guest_cart(self, request: Request, user_id: UUID) -> None:
        """
        合併訪客購物車到會員購物車

        從 Request 中提取 guest token，若存在則執行合併。
        合併失敗不應中斷登入流程。

        Args:
            request: FastAPI Request 物件（用於提取 Cookie 中的 guest token）
            user_id: 會員 UUID
        """
        pass
