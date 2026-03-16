"""
Cart Merge Use Case

處理訪客購物車與用戶購物車合併的業務邏輯
"""
import uuid
from typing import List, Optional

from modules.cart.domain.repository import ICartRepository
from modules.cart.domain.entities import CartItemResponse, CartItemCreate


class MergeCartUseCase:
    """合併訪客購物車到用戶購物車的業務邏輯"""

    def __init__(self, repository: ICartRepository):
        """
        初始化 Use Case

        Args:
            repository: SQLCartRepository（必須是用戶購物車）
        """
        self.repository = repository

    async def execute(
        self,
        owner_id: str,
        guest_items: List[dict]
    ) -> List[CartItemResponse]:
        """
        執行購物車合併

        業務邏輯:
        - 遍歷訪客商品列表
        - 若用戶購物車已有該商品 → 更新數量（累加）
        - 若用戶購物車無該商品 → 新增商品
        - 返回合併後的購物車

        Args:
            owner_id: 用戶 ID（UUID 字串）
            guest_items: 訪客商品列表
                [
                    {
                        "product_id": "uuid",
                        "quantity": 2
                    },
                    ...
                ]

        Returns:
            List[CartItemResponse]: 合併後的購物車項目列表

        Raises:
            ValueError: 無效的商品數據
        """
        if not guest_items:
            # 訪客購物車為空，直接返回用戶購物車
            return await self.repository.get_cart(owner_id)

        # 遍歷訪客商品進行合併
        for item in guest_items:
            try:
                product_id = uuid.UUID(item.get('product_id')) if isinstance(item.get('product_id'), str) else item.get('product_id')
                quantity = item.get('quantity', 0)

                if quantity <= 0:
                    continue  # 跳過無效數量

                # 檢查用戶購物車中是否已有該商品
                existing_item = await self.repository.get_item(owner_id, product_id)

                if existing_item:
                    # 商品已存在，累加數量
                    new_quantity = existing_item.quantity + quantity
                    await self.repository.update_quantity(owner_id, product_id, new_quantity)
                else:
                    # 商品不存在，新增到購物車
                    await self.repository.add_item(owner_id, product_id, quantity)

            except (ValueError, TypeError) as e:
                # 無效的商品數據，記錄並跳過
                print(f"Failed to merge item {item}: {e}")
                continue

        # 返回合併後的購物車
        return await self.repository.get_cart(owner_id)
