from abc import ABC, abstractmethod
from typing import List, Optional
import uuid

from modules.cart.domain.entities import CartItemResponse, CartItemCreate


class ICartRepository(ABC):
    """
    購物車 Repository 介面

    Design Rules:
    1. 所有方法都是抽象的，由子類實作
    2. owner_id 可以是 guest_token 或 str(user_id)
    3. 所有方法都是 async，支援非同步 I/O
    4. 支援雙重識別：會員 (user_id) 或訪客 (guest_token)
    5. 購物車不儲存價格，價格在顯示時動態查詢 Product
    """

    @abstractmethod
    async def add_item(
        self,
        owner_id: str,
        product_id: uuid.UUID,
        quantity: int
    ) -> CartItemResponse:
        """
        新增商品到購物車

        邏輯:
        - 若商品已存在，累加數量
        - 若商品不存在，新增項目
        - 不儲存價格（顯示時動態查詢）

        Args:
            owner_id: 擁有者識別（guest_token 或 str(user_id)）
            product_id: 商品 UUID
            quantity: 數量（必須 > 0）

        Returns:
            CartItemResponse: 更新後的購物車項目

        Raises:
            ValueError: 數量 <= 0
        """
        pass

    @abstractmethod
    async def update_quantity(
        self,
        owner_id: str,
        product_id: uuid.UUID,
        quantity: int
    ) -> CartItemResponse:
        """
        更新商品數量

        Args:
            owner_id: 擁有者識別
            product_id: 商品 UUID
            quantity: 新數量 (必須 > 0)

        Returns:
            CartItemResponse: 更新後的購物車項目

        Raises:
            ValueError: 數量 <= 0 或商品不存在
        """
        pass

    @abstractmethod
    async def get_cart(
        self,
        owner_id: str
    ) -> List[CartItemResponse]:
        """
        取得完整購物車

        Args:
            owner_id: 擁有者識別

        Returns:
            List[CartItemResponse]: 購物車項目列表（可能為空）
        """
        pass

    @abstractmethod
    async def get_item(
        self,
        owner_id: str,
        product_id: uuid.UUID
    ) -> Optional[CartItemResponse]:
        """
        查詢單一商品

        Args:
            owner_id: 擁有者識別
            product_id: 商品 UUID

        Returns:
            Optional[CartItemResponse]: 購物車項目，若不存在則回傳 None
        """
        pass

    @abstractmethod
    async def remove_item(
        self,
        owner_id: str,
        product_id: uuid.UUID
    ) -> None:
        """
        移除商品

        Args:
            owner_id: 擁有者識別
            product_id: 商品 UUID
        """
        pass

    @abstractmethod
    async def clear_cart(
        self,
        owner_id: str
    ) -> None:
        """
        清空購物車

        Args:
            owner_id: 擁有者識別
        """
        pass

    @abstractmethod
    async def batch_add_items(
        self,
        owner_id: str,
        items: List[CartItemCreate]
    ) -> List[CartItemResponse]:
        """
        批量新增商品 (merge cart 使用)

        Args:
            owner_id: 使用者識別
            items: 購物車項目列表

        Returns:
            List[CartItemResponse]: 更新後的購物車項目列表
        """
        pass


