"""
SQL-based Cart Repository Implementation

This module implements the CartRepository interface for member carts using PostgreSQL.
Member carts are persistent and stored in the database.

Storage Strategy:
- Uses PostgreSQL tables: carts and cart_items
- Each member has one cart (identified by user_id)
- Cart items are linked to cart via cart_id
- Supports full CRUD operations with proper transaction handling
"""

from typing import List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from modules.cart.domain.repository import ICartRepository
from modules.cart.domain.entities import CartItemResponse, CartItemCreate
from modules.cart.infrastructure.models import CartModel, CartItemModel
from modules.product.infrastructure.repository import SqlAlchemyProductRepository


class SQLCartRepository(ICartRepository):
    """會員購物車的 PostgreSQL 實作"""

    def __init__(self, db: AsyncSession):
        """
        初始化 SQL Cart Repository

        Args:
            db: SQLAlchemy AsyncSession instance
        """
        self.db = db

    async def _get_or_create_cart(self, user_id: uuid.UUID) -> CartModel:
        """
        取得或建立會員購物車

        Args:
            user_id: 會員 UUID

        Returns:
            CartModel: 購物車實體
        """
        # 查詢現有購物車
        stmt = select(CartModel).where(CartModel.user_id == user_id)
        result = await self.db.execute(stmt)
        cart = result.scalar_one_or_none()

        if not cart:
            # 建立新購物車
            cart = CartModel(user_id=user_id, guest_token=None)
            self.db.add(cart)
            await self.db.flush()  # 取得 cart.id

        return cart

    async def _find_item(
        self, cart_id: uuid.UUID, product_id: uuid.UUID
    ) -> Optional[CartItemModel]:
        """
        查詢購物車中的特定商品

        Args:
            cart_id: 購物車 UUID
            product_id: 商品 UUID

        Returns:
            Optional[CartItemModel]: 購物車項目，若不存在則回傳 None
        """
        stmt = select(CartItemModel).where(
            CartItemModel.cart_id == cart_id, CartItemModel.product_id == product_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _to_response(self, item: CartItemModel) -> CartItemResponse:
        """
        將 CartItemModel 轉換為 CartItemResponse，並包含商品信息

        Args:
            item: CartItemModel 實體

        Returns:
            CartItemResponse: Pydantic response schema
        """
        # 查詢商品信息
        product_repo = SqlAlchemyProductRepository(self.db)
        product = await product_repo.get_by_id(item.product_id)

        # 計算小計
        product_price = float(product.price) if product else 0.0
        subtotal = product_price * item.quantity

        # 取得第一張圖片 URL
        image_url = None
        if product and product.images:
            primary_image = next(
                (img for img in product.images if img.is_primary), None
            )
            image_url = (
                (primary_image or product.images[0]).url
                if (primary_image or product.images)
                else None
            )

        return CartItemResponse(
            id=item.id,
            cart_id=item.cart_id,
            product_id=item.product_id,
            quantity=item.quantity,
            product_name=(
                product.name if product else f"Unknown Product ({item.product_id})"
            ),
            unit_price=product_price,
            subtotal=subtotal,
            image_url=image_url,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    async def add_item(
        self, owner_id: str, product_id: uuid.UUID, quantity: int
    ) -> CartItemResponse:
        """
        新增商品到購物車（若已存在則累加數量）

        Args:
            owner_id: 會員 ID（UUID 字串）
            product_id: 商品 UUID
            quantity: 數量（必須 > 0）

        Returns:
            CartItemResponse: 更新後的購物車項目

        Raises:
            ValueError: 數量 <= 0
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        user_id = uuid.UUID(owner_id)

        # 1. 取得或建立購物車
        cart = await self._get_or_create_cart(user_id)

        # 2. 查詢商品是否已存在
        existing_item = await self._find_item(cart.id, product_id)

        if existing_item:
            # 數量累加
            existing_item.quantity += quantity
            await self.db.flush()
            await self.db.refresh(existing_item)
            return await self._to_response(existing_item)
        else:
            # 新增商品
            new_item = CartItemModel(
                cart_id=cart.id, product_id=product_id, quantity=quantity
            )
            self.db.add(new_item)
            await self.db.flush()
            await self.db.refresh(new_item)
            return await self._to_response(new_item)

    async def update_quantity(
        self, owner_id: str, product_id: uuid.UUID, quantity: int
    ) -> CartItemResponse:
        """
        更新商品數量

        Args:
            owner_id: 會員 ID（UUID 字串）
            product_id: 商品 UUID
            quantity: 新數量（必須 > 0）

        Returns:
            CartItemResponse: 更新後的購物車項目

        Raises:
            ValueError: 數量 <= 0 或商品不存在
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        user_id = uuid.UUID(owner_id)

        # 取得購物車
        cart = await self._get_or_create_cart(user_id)

        # 查詢商品
        item = await self._find_item(cart.id, product_id)
        if not item:
            raise ValueError(f"Product {product_id} not found in cart")

        # 更新數量
        item.quantity = quantity
        await self.db.flush()
        await self.db.refresh(item)

        return await self._to_response(item)

    async def get_cart(self, owner_id: str) -> List[CartItemResponse]:
        """
        取得購物車所有商品

        Args:
            owner_id: 會員 ID（UUID 字串）

        Returns:
            List[CartItemResponse]: 購物車項目列表（可能為空）
        """
        user_id = uuid.UUID(owner_id)

        # 查詢購物車（含所有項目）
        stmt = (
            select(CartModel)
            .where(CartModel.user_id == user_id)
            .options(selectinload(CartModel.items))  # 預先載入 items
        )
        result = await self.db.execute(stmt)
        cart = result.scalar_one_or_none()

        if not cart or not cart.items:
            return []

        # 轉換為 Response
        return [await self._to_response(item) for item in cart.items]

    async def get_item(
        self, owner_id: str, product_id: uuid.UUID
    ) -> Optional[CartItemResponse]:
        """
        查詢單一商品

        Args:
            owner_id: 會員 ID（UUID 字串）
            product_id: 商品 UUID

        Returns:
            Optional[CartItemResponse]: 購物車項目，若不存在則回傳 None
        """
        user_id = uuid.UUID(owner_id)

        # 取得購物車
        cart = await self._get_or_create_cart(user_id)

        # 查詢商品
        item = await self._find_item(cart.id, product_id)

        return await self._to_response(item) if item else None

    async def remove_item(self, owner_id: str, product_id: uuid.UUID) -> None:
        """
        移除商品

        Args:
            owner_id: 會員 ID（UUID 字串）
            product_id: 商品 UUID
        """
        user_id = uuid.UUID(owner_id)

        # 取得購物車
        cart = await self._get_or_create_cart(user_id)

        # 刪除商品
        stmt = delete(CartItemModel).where(
            CartItemModel.cart_id == cart.id, CartItemModel.product_id == product_id
        )
        await self.db.execute(stmt)
        await self.db.flush()

    async def clear_cart(self, owner_id: str) -> None:
        """
        清空購物車

        Args:
            owner_id: 會員 ID（UUID 字串）
        """
        user_id = uuid.UUID(owner_id)

        # 取得購物車
        cart = await self._get_or_create_cart(user_id)

        # 刪除所有項目
        stmt = delete(CartItemModel).where(CartItemModel.cart_id == cart.id)
        await self.db.execute(stmt)
        await self.db.flush()

    async def batch_add_items(
        self, owner_id: str, items: List[CartItemCreate]
    ) -> List[CartItemResponse]:
        """
        批量新增商品（merge cart 使用）

        Args:
            owner_id: 會員 ID（UUID 字串）
            items: 購物車項目列表

        Returns:
            List[CartItemResponse]: 更新後的購物車項目列表
        """
        result = []
        for item in items:
            updated_item = await self.add_item(owner_id, item.product_id, item.quantity)
            result.append(updated_item)

        return result
