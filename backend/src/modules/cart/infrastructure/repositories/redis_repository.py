"""
Redis-based Cart Repository Implementation

This module implements the CartRepository interface for guest carts using Redis as storage.
Guest carts are temporary and expire after 7 days of inactivity.

Storage Strategy:
- Uses Redis Hash: Key = "cart:{owner_id}", Field = product_id, Value = JSON data
- Each cart item contains: product_id, quantity, created_at, updated_at
- Price is NOT stored (queried dynamically from Product when displaying)
- TTL is reset on every operation to maintain 7-day expiration
"""

from typing import List, Optional
import json
import uuid
from datetime import datetime, timedelta, timezone
from redis.asyncio import Redis

from modules.cart.domain.repository import ICartRepository
from modules.cart.domain.entities import CartItemResponse, CartItemCreate


class RedisCartRepository(ICartRepository):
    """訪客購物車的 Redis 實作"""

    def __init__(self, redis_client: Redis):
        """
        初始化 Redis Cart Repository

        Args:
            redis_client: Redis async client instance
        """
        self.redis = redis_client
        self.ttl = int(timedelta(days=7).total_seconds())  # 訪客購物車保留 7 天

    def _cart_key(self, owner_id: str) -> str:
        """
        生成 Redis Key

        Args:
            owner_id: 擁有者識別（guest_token 或 str(user_id)）

        Returns:
            str: Redis key in format "cart:{owner_id}"
        """
        return f"cart:{owner_id}"

    def _serialize_item(self, product_id: uuid.UUID, quantity: int,
                        created_at: datetime, updated_at: datetime) -> str:
        """
        將購物車項目序列化為 JSON

        Args:
            product_id: 商品 UUID
            quantity: 數量
            created_at: 建立時間
            updated_at: 更新時間

        Returns:
            str: JSON 格式字串
        """
        data = {
            "product_id": str(product_id),
            "quantity": quantity,
            "created_at": created_at.isoformat(),
            "updated_at": updated_at.isoformat()
        }
        return json.dumps(data)

    def _deserialize_item(self, raw_data: str) -> dict:
        """
        將 JSON 反序列化為字典

        Args:
            raw_data: JSON 格式字串

        Returns:
            dict: 包含 product_id, quantity, created_at, updated_at 的字典
        """
        data = json.loads(raw_data)
        return {
            "product_id": uuid.UUID(data["product_id"]),
            "quantity": data["quantity"],
            "created_at": datetime.fromisoformat(data["created_at"]),
            "updated_at": datetime.fromisoformat(data["updated_at"])
        }

    async def add_item(
        self,
        owner_id: str,
        product_id: uuid.UUID,
        quantity: int
    ) -> CartItemResponse:
        """
        新增商品到購物車（若已存在則累加數量）

        Args:
            owner_id: 擁有者識別（guest_token 或 str(user_id)）
            product_id: 商品 UUID
            quantity: 數量（必須 > 0）

        Returns:
            CartItemResponse: 更新後的購物車項目

        Raises:
            ValueError: 數量 <= 0
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        key = self._cart_key(owner_id)
        product_id_str = str(product_id)

        # 取得現有商品資料
        existing = await self.redis.hget(key, product_id_str)

        now = datetime.now(timezone.utc)

        if existing:
            # 數量累加
            data = self._deserialize_item(existing)
            new_quantity = data["quantity"] + quantity
            created_at = data["created_at"]
            updated_at = now
        else:
            # 新增商品
            new_quantity = quantity
            created_at = now
            updated_at = now

        # 儲存至 Redis Hash
        serialized = self._serialize_item(product_id, new_quantity, created_at, updated_at)
        await self.redis.hset(key, product_id_str, serialized)

        # 設定過期時間
        await self.redis.expire(key, self.ttl)

        # 生成假的 cart_id 和 item_id (Redis 沒有這些概念)
        item_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"{owner_id}:{product_id_str}")
        cart_id = uuid.uuid5(uuid.NAMESPACE_DNS, owner_id)

        return CartItemResponse(
            id=item_id,
            cart_id=cart_id,
            product_id=product_id,
            quantity=new_quantity,
            created_at=created_at,
            updated_at=updated_at
        )

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
            quantity: 新數量（必須 > 0）

        Returns:
            CartItemResponse: 更新後的購物車項目

        Raises:
            ValueError: 數量 <= 0 或商品不存在
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        key = self._cart_key(owner_id)
        product_id_str = str(product_id)

        existing = await self.redis.hget(key, product_id_str)
        if not existing:
            raise ValueError(f"Product {product_id} not found in cart")

        data = self._deserialize_item(existing)
        created_at = data["created_at"]
        updated_at = datetime.now(timezone.utc)

        # 更新數量
        serialized = self._serialize_item(product_id, quantity, created_at, updated_at)
        await self.redis.hset(key, product_id_str, serialized)
        await self.redis.expire(key, self.ttl)

        # 生成假的 IDs
        item_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"{owner_id}:{product_id_str}")
        cart_id = uuid.uuid5(uuid.NAMESPACE_DNS, owner_id)

        return CartItemResponse(
            id=item_id,
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity,
            created_at=created_at,
            updated_at=updated_at
        )

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
        key = self._cart_key(owner_id)
        product_id_str = str(product_id)
        await self.redis.hdel(key, product_id_str)

    async def get_cart(
        self,
        owner_id: str
    ) -> List[CartItemResponse]:
        """
        取得購物車所有商品

        Args:
            owner_id: 擁有者識別

        Returns:
            List[CartItemResponse]: 購物車項目列表（可能為空）
        """
        key = self._cart_key(owner_id)
        items_data = await self.redis.hgetall(key)

        if not items_data:
            return []

        cart_id = uuid.uuid5(uuid.NAMESPACE_DNS, owner_id)
        items = []

        for product_id_str, raw_data in items_data.items():
            data = self._deserialize_item(raw_data)
            item_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"{owner_id}:{product_id_str}")

            items.append(CartItemResponse(
                id=item_id,
                cart_id=cart_id,
                product_id=data["product_id"],
                quantity=data["quantity"],
                created_at=data["created_at"],
                updated_at=data["updated_at"]
            ))

        return items

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
        key = self._cart_key(owner_id)
        product_id_str = str(product_id)

        existing = await self.redis.hget(key, product_id_str)
        if not existing:
            return None

        data = self._deserialize_item(existing)
        item_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"{owner_id}:{product_id_str}")
        cart_id = uuid.uuid5(uuid.NAMESPACE_DNS, owner_id)

        return CartItemResponse(
            id=item_id,
            cart_id=cart_id,
            product_id=data["product_id"],
            quantity=data["quantity"],
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )

    async def clear_cart(
        self,
        owner_id: str
    ) -> None:
        """
        清空購物車

        Args:
            owner_id: 擁有者識別
        """
        key = self._cart_key(owner_id)
        await self.redis.delete(key)

    async def batch_add_items(
        self,
        owner_id: str,
        items: List[CartItemCreate]
    ) -> List[CartItemResponse]:
        """
        批量新增商品（merge cart 使用）
        使用 Redis Pipeline 優化，減少網路來回次數。

        Args:
            owner_id: 擁有者識別
            items: 購物車項目列表

        Returns:
            List[CartItemResponse]: 更新後的購物車項目列表
        """
        key = self._cart_key(owner_id)
        now = datetime.now(timezone.utc)
        result = []
        
        # 1. 使用 Pipeline 一次讀取所有商品的現有狀態 (HGET)
        async with self.redis.pipeline(transaction=True) as pipe:
            for item in items:
                pipe.hget(key, str(item.product_id))
            existing_values = await pipe.execute()
        
        # 2. 在記憶體中計算新狀態
        updates = {} # product_id_str -> serialized_data
        
        for i, item in enumerate(items):
            product_id_str = str(item.product_id)
            existing = existing_values[i]
            
            if existing:
                # 累加數量
                data = self._deserialize_item(existing)
                new_quantity = data["quantity"] + item.quantity
                created_at = data["created_at"]
                updated_at = now
            else:
                # 新增
                new_quantity = item.quantity
                created_at = now
                updated_at = now
                
            serialized = self._serialize_item(
                item.product_id, new_quantity, created_at, updated_at
            )
            updates[product_id_str] = serialized
            
            # 建構回傳物件
            item_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"{owner_id}:{product_id_str}")
            cart_id = uuid.uuid5(uuid.NAMESPACE_DNS, owner_id)
            
            result.append(CartItemResponse(
                id=item_id,
                cart_id=cart_id,
                product_id=item.product_id,
                quantity=new_quantity,
                created_at=created_at,
                updated_at=updated_at
            ))
            
        # 3. 使用 Pipeline 一次寫入所有更新 (HSET) 並設定過期時間
        if updates:
            async with self.redis.pipeline(transaction=True) as pipe:
                # 雖然 hset 支援多個 mapping, 但 python redis client 的 hset 
                # 可以直接傳入 mapping 字典 {field: value, ...}
                pipe.hset(key, mapping=updates)
                pipe.expire(key, self.ttl)
                await pipe.execute()

        return result

