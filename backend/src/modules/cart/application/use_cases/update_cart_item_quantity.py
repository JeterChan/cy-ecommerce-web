import uuid

from modules.cart.domain.repository import ICartRepository
from modules.cart.domain.entities import CartItemResponse
from modules.cart.domain.ports import IProductInfoPort
from modules.cart.domain.exceptions import InsufficientStockException


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

        Raises:
            InsufficientStockException: 庫存不足
            ValueError: 數量 <= 0 或商品不存在
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        product = await self.product_port.get_product_info(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        if quantity > product.stock_quantity:
            raise InsufficientStockException(
                product_name=product.name,
                requested=quantity,
                available=product.stock_quantity
            )

        return await self.repository.update_quantity(owner_id, product_id, quantity)
