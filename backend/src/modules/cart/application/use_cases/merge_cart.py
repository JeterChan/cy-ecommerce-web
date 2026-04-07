import uuid
from typing import List

from modules.cart.domain.repository import ICartRepository
from modules.cart.domain.entities import CartItemResponse


class MergeCartUseCase:
    """合併訪客購物車到用戶購物車的業務邏輯"""

    def __init__(self, repository: ICartRepository):
        """
        Args:
            repository: SQLCartRepository（必須是用戶購物車）
        """
        self.repository = repository

    async def execute(
        self, owner_id: str, guest_items: List[dict]
    ) -> List[CartItemResponse]:
        """
        執行購物車合併

        業務邏輯:
        - 遍歷訪客商品列表
        - 若用戶購物車已有該商品 → 更新數量（累加）
        - 若用戶購物車無該商品 → 新增商品
        - 返回合併後的購物車

        Raises:
            ValueError: 無效的商品數據
        """
        if not guest_items:
            return await self.repository.get_cart(owner_id)

        for item in guest_items:
            try:
                product_id = (
                    uuid.UUID(item.get("product_id"))
                    if isinstance(item.get("product_id"), str)
                    else item.get("product_id")
                )
                quantity = item.get("quantity", 0)

                if quantity <= 0:
                    continue

                existing_item = await self.repository.get_item(owner_id, product_id)

                if existing_item:
                    new_quantity = existing_item.quantity + quantity
                    await self.repository.update_quantity(
                        owner_id, product_id, new_quantity
                    )
                else:
                    await self.repository.add_item(owner_id, product_id, quantity)

            except (ValueError, TypeError) as e:
                print(f"Failed to merge item {item}: {e}")
                continue

        return await self.repository.get_cart(owner_id)
