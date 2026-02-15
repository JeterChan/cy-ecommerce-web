from abc import ABC, abstractmethod
from typing import List, Optional
import uuid

from modules.cart.domain.schemas import CartItemBase, CartItemCreate

class CartRepository(ABC):
    """

    Design Rules:
    1. 所有方法都是抽象的，由子類實作
    2. owner_id 可以是 guest_token or user_id (UUID -> str)
    3. 所有方法的是 async, 支援非同步 I/O
    """

    @abstractmethod
    async def add_item(
        self,
        owner_id: str,
        product_id: uuid.UUID,
        quantity: int
    ) -> CartItemBase:
        """
            新增商品到購物車

            邏輯:
            - 若商品已存在，累加數量
            - 若商品不存在，新增項目

            Args:
                owner_id: 擁有者識別（guest_token 或 str(user_id)）
                product_id: 商品 UUID
                quantity: 數量（必須 > 0）

            Returns:
                CartItemBase: 更新後的購物車項目

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
    ) -> CartItemBase:
        """
        更新商品數量

        Args:
            owner_id: 擁有者識別
            product_id: 商品 UUID
            quantity: 新數量 (必須 >0)

        Returns:
            CartItemBase: 更新後的購物車項目

        Raises:
            ValueError: 數量 <= 0 or 商品不存在
        """
        pass

    @abstractmethod
    async def get_cart(
        self,
        owner_id: str
    )->List[CartItemBase]:
        """
        取得完整購物車
        :param
            owner_id: 擁有者識別
        :return:
            List[CartItemBase]:購物車項目列表(可能為空)
        """
        pass

    @abstractmethod
    async def get_item(
        self,
        owner_id: str,
        product_id: uuid.UUID
    ) -> Optional[CartItemBase]:
        """
        查詢單一商品

        :param owner_id: 擁有者識別
        :param product_id: 商品 UUID
        :return:
            Optional[CartItemBase]: 購物車項目, 若不存在則回傳 None
        """
        pass

    @abstractmethod
    async def clear_cart(
        self,
        owner_id: str
    ) -> None:
        """
        清空購物車

        :param owner_id: 擁有者辨別
        :return:
        """

    @abstractmethod
    async def batch_add_items(
        self,
        owner_id: str,
        items: List[CartItemCreate]
    ) -> List[CartItemBase]:
        """
        批量新增商品 (merge cart 使用)
        :param owner_id: 使用者識別
        :param items: 購物車項目列表
        :return: List[CartItemBase]: 更新後的購物超項目列表
        """
        pass