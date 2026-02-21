"""
Product DTOs (Data Transfer Objects)

區分 Input 和 Output DTOs 以提高程式碼清晰度
"""
from .inputs import ProductCreateDTO, ProductUpdateDTO, ProductStockAdjustDTO
from .outputs import ProductResponseDTO, ProductListItemDTO

__all__ = [
    # Input DTOs
    "ProductCreateDTO",
    "ProductUpdateDTO",
    "ProductStockAdjustDTO",

    # Output DTOs
    "ProductResponseDTO",
    "ProductListItemDTO",
]

