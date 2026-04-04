import uuid

from modules.cart.domain.repository import ICartRepository
from modules.cart.domain.entities import CartItemResponse
from modules.cart.domain.ports import IProductInfoPort
from modules.cart.domain.exceptions import InsufficientStockException


class AddToCartUseCase:
    """新增商品到購物車的業務邏輯"""

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
        執行新增商品到購物車

        業務邏輯:
        - 數量必須大於 0
        - 讀取商品資訊（不加鎖，僅進行初步校驗）
        - 若商品已存在購物車，則校驗總數量不超過當下庫存
        - 若校驗通過，則更新購物車

        Raises:
            InsufficientStockException: 庫存不足
            ValueError: 數量 <= 0 或商品不存在
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        product = await self.product_port.get_product_info(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        if not product.is_active:
            raise ValueError(f"Product {product_id} not available")

        existing_item = await self.repository.get_item(owner_id, product_id)
        current_quantity = existing_item.quantity if existing_item else 0
        new_total_quantity = current_quantity + quantity

        if new_total_quantity > product.stock_quantity:
            raise InsufficientStockException(
                product_name=product.name,
                requested=new_total_quantity,
                available=product.stock_quantity
            )

        return await self.repository.add_item(owner_id, product_id, quantity)
