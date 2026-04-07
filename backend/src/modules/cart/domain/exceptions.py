from shared.exceptions.base import DomainException


class InsufficientStockException(DomainException):
    """當商品庫存不足以滿足購物車請求時拋出"""

    def __init__(self, product_name: str, requested: int, available: int):
        self.product_name = product_name
        self.requested = requested
        self.available = available
        self.message = (
            f"Insufficient stock for product '{product_name}'. "
            f"Requested: {requested}, Available: {available}"
        )
        super().__init__(self.message)
