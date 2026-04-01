"""
Cart Command Use Cases

處理修改購物車資料的業務邏輯（Commands）
包含：新增商品、更新數量、移除商品、清空購物車
"""
import uuid
from typing import List

from modules.cart.domain.repository import ICartRepository
from modules.cart.domain.entities import CartItemResponse, CartItemCreate
from modules.cart.domain.ports import IProductInfoPort
from modules.cart.domain.exceptions import InsufficientStockException


class AddToCartUseCase:
    """新增商品到購物車的業務邏輯"""

    def __init__(self, repository: ICartRepository, product_port: IProductInfoPort):
        """
        初始化 Use Case

        Args:
            repository: CartRepository 實作
            product_port: 商品資訊 Port 實作
        """
        self.repository = repository
        self.product_port = product_port

    async def execute(
        self,
        owner_id: str,
        product_id: uuid.UUID,
        quantity: int
    ) -> CartItemResponse:
        """
        執行新增商品到購物車

        業務邏輯:
        - 數量必須大於 0
        - 讀取商品資訊（不加鎖，僅進行初步校驗）
        - 若商品已存在購物車，則校驗總數量不超過當下庫存
        - 若校驗通過，則更新購物車

        Args:
            owner_id: 擁有者識別
            product_id: 商品 UUID
            quantity: 數量（必須 > 0）

        Returns:
            CartItemResponse: 更新後的購物車項目

        Raises:
            InsufficientStockException: 庫存不足
            ValueError: 數量 <= 0 或商品不存在
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        # 1. 取得商品資訊 (一般的 SELECT)
        product = await self.product_port.get_product_info(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        # 2. 取得購物車現有數量
        existing_item = await self.repository.get_item(owner_id, product_id)
        current_quantity = existing_item.quantity if existing_item else 0
        new_total_quantity = current_quantity + quantity

        # 3. 庫存校驗 (Soft Check)
        if new_total_quantity > product.stock_quantity:
            raise InsufficientStockException(
                product_name=product.name,
                requested=new_total_quantity,
                available=product.stock_quantity
            )

        # 4. 執行新增/更新
        return await self.repository.add_item(owner_id, product_id, quantity)


class UpdateCartItemQuantityUseCase:
    """更新購物車商品數量的業務邏輯"""

    def __init__(self, repository: ICartRepository, product_port: IProductInfoPort):
        self.repository = repository
        self.product_port = product_port

    async def execute(
        self,
        owner_id: str,
        product_id: uuid.UUID,
        quantity: int
    ) -> CartItemResponse:
        """
        執行更新購物車商品數量

        Args:
            owner_id: 擁有者識別
            product_id: 商品 UUID
            quantity: 新數量（必須 > 0）

        Returns:
            CartItemResponse: 更新後的購物車項目

        Raises:
            InsufficientStockException: 庫存不足
            ValueError: 數量 <= 0 或商品不存在
        """
        # 業務驗證
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        # 1. 取得商品資訊
        product = await self.product_port.get_product_info(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        # 2. 庫存校驗 (Soft Check)
        if quantity > product.stock_quantity:
            raise InsufficientStockException(
                product_name=product.name,
                requested=quantity,
                available=product.stock_quantity
            )

        # 執行操作
        return await self.repository.update_quantity(owner_id, product_id, quantity)


class RemoveFromCartUseCase:
    """從購物車移除商品的業務邏輯"""

    def __init__(self, repository: ICartRepository):
        self.repository = repository

    async def execute(
        self,
        owner_id: str,
        product_id: uuid.UUID
    ) -> None:
        """
        執行從購物車移除商品

        Args:
            owner_id: 擁有者識別
            product_id: 商品 UUID
        """
        await self.repository.remove_item(owner_id, product_id)


class ClearCartUseCase:
    """清空購物車的業務邏輯"""

    def __init__(self, repository: ICartRepository):
        self.repository = repository

    async def execute(self, owner_id: str) -> None:
        """
        執行清空購物車

        Args:
            owner_id: 擁有者識別
        """
        await self.repository.clear_cart(owner_id)


class BatchAddToCartUseCase:
    """批量新增商品到購物車的業務邏輯"""

    def __init__(self, repository: ICartRepository):
        self.repository = repository

    async def execute(
        self,
        owner_id: str,
        items: List[CartItemCreate]
    ) -> List[CartItemResponse]:
        """
        執行批量新增商品到購物車

        使用場景: 購物車合併（Phase 5）

        Args:
            owner_id: 擁有者識別
            items: 購物車項目列表

        Returns:
            List[CartItemResponse]: 更新後的購物車項目列表
        """
        return await self.repository.batch_add_items(owner_id, items)
