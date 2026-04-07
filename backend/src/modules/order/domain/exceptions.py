from shared.exceptions.base import DomainException


class InsufficientStockException(DomainException):
    def __init__(self, product_name: str, requested: int, available: int):
        self.product_name = product_name
        self.requested = requested
        self.available = available
        super().__init__(
            f"商品 '{product_name}' 庫存不足。請求數量: {requested}, 可用數量: {available}"
        )


class PriceChangedException(DomainException):
    def __init__(self, product_name: str, old_price: float, new_price: float):
        self.product_name = product_name
        self.old_price = old_price
        self.new_price = new_price
        super().__init__(
            f"商品 '{product_name}' 價格已變動 (由 {old_price} 變更為 {new_price})。請重新確認後再結帳。"
        )


class EmptyCartException(DomainException):
    def __init__(self):
        super().__init__("購物車是空的，無法結帳。")
