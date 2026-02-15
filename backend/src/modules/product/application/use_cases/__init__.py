"""
Product Use Cases

匯出所有 Product 相關的 Use Cases
"""
from .product_commands import (
    CreateProductUseCase,
    UpdateProductUseCase,
    DeleteProductUseCase,
    ToggleProductActiveUseCase,
    AdjustProductStockUseCase,
)
from .product_queries import (
    GetProductUseCase,
    ListProductsUseCase,
)

__all__ = [
    # Commands (修改資料)
    "CreateProductUseCase",
    "UpdateProductUseCase",
    "DeleteProductUseCase",
    "ToggleProductActiveUseCase",
    "AdjustProductStockUseCase",

    # Queries (查詢資料)
    "GetProductUseCase",
    "ListProductsUseCase",
]

