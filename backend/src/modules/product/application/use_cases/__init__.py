"""
Product Use Cases

匯出所有 Product 相關的 Use Cases
"""

from .create_product import CreateProductUseCase
from .update_product import UpdateProductUseCase
from .delete_product import DeleteProductUseCase
from .toggle_product_active import ToggleProductActiveUseCase
from .adjust_product_stock import AdjustProductStockUseCase
from .get_product import GetProductUseCase
from .list_products import ListProductsUseCase
from .list_products_admin import ListProductsAdminUseCase
from .get_dashboard_stats import GetDashboardStatsUseCase

__all__ = [
    # Commands
    "CreateProductUseCase",
    "UpdateProductUseCase",
    "DeleteProductUseCase",
    "ToggleProductActiveUseCase",
    "AdjustProductStockUseCase",
    # Queries
    "GetProductUseCase",
    "ListProductsUseCase",
    "ListProductsAdminUseCase",
    "GetDashboardStatsUseCase",
]
