"""
Product API Routes

定義 Product 模組的 HTTP API 端點
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from infrastructure.database import get_db
from modules.product.infrastructure.repository import SqlAlchemyProductRepository
from modules.product.application.use_cases import (
    CreateProductUseCase,
    GetProductUseCase,
    ListProductsUseCase,
    UpdateProductUseCase,
    DeleteProductUseCase,
    ToggleProductActiveUseCase,
    AdjustProductStockUseCase,
)
from modules.product.application.dtos import (
    ProductCreateDTO,
    ProductUpdateDTO,
    ProductResponseDTO,
    ProductStockAdjustDTO,
)


router = APIRouter(prefix="/products", tags=["Products"])


# ==================== CRUD 操作 ====================

@router.post(
    "",
    response_model=ProductResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="建立商品",
    description="建立新商品"
)
async def create_product(
    data: ProductCreateDTO,
    db: AsyncSession = Depends(get_db)
) -> ProductResponseDTO:
    """
    建立新商品

    - **name**: 商品名稱 (必填)
    - **price**: 商品價格 (必填，大於 0)
    - **stock_quantity**: 庫存數量 (必填，≥ 0)
    """
    try:
        use_case = CreateProductUseCase(SqlAlchemyProductRepository(db))
        product = await use_case.execute(data)
        return ProductResponseDTO.model_validate(product)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{product_id}",
    response_model=ProductResponseDTO,
    summary="取得單一商品",
    description="根據 UUID 取得商品詳細資訊"
)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> ProductResponseDTO:
    """取得指定 UUID 的商品詳細資訊"""
    try:
        use_case = GetProductUseCase(SqlAlchemyProductRepository(db))
        product = await use_case.execute(product_id)
        return ProductResponseDTO.model_validate(product)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "",
    response_model=List[ProductResponseDTO],
    summary="列出商品清單",
    description="列出商品清單，支援分頁和篩選"
)
async def list_products(
    skip: int = Query(default=0, ge=0, description="略過的筆數"),
    limit: int = Query(default=100, ge=1, le=1000, description="取得的筆數上限"),
    is_active: Optional[bool] = Query(default=None, description="篩選上架狀態"),
    db: AsyncSession = Depends(get_db)
) -> List[ProductResponseDTO]:
    """
    列出商品清單

    - **skip**: 略過的筆數
    - **limit**: 取得的筆數上限 (最大 1000)
    - **is_active**: 篩選上架狀態 (null=全部, true=上架, false=下架)
    """
    use_case = ListProductsUseCase(SqlAlchemyProductRepository(db))
    products = await use_case.execute(skip=skip, limit=limit, is_active=is_active)
    return [ProductResponseDTO.model_validate(p) for p in products]


@router.put(
    "/{product_id}",
    response_model=ProductResponseDTO,
    summary="更新商品",
    description="更新商品資訊（部分更新）"
)
async def update_product(
    product_id: UUID,
    data: ProductUpdateDTO,
    db: AsyncSession = Depends(get_db)
) -> ProductResponseDTO:
    """更新商品資訊 (部分更新)"""
    try:
        use_case = UpdateProductUseCase(SqlAlchemyProductRepository(db))
        product = await use_case.execute(product_id, data)
        return ProductResponseDTO.model_validate(product)
    except ValueError as e:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "不存在" in str(e)
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=status_code, detail=str(e))


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="刪除商品",
    description="刪除指定的商品"
)
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> None:
    """刪除指定 UUID 的商品"""
    try:
        use_case = DeleteProductUseCase(SqlAlchemyProductRepository(db))
        await use_case.execute(product_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ==================== 業務操作 ====================

@router.post(
    "/{product_id}/toggle-active",
    response_model=ProductResponseDTO,
    summary="切換商品上下架狀態",
    description="切換商品的上架/下架狀態"
)
async def toggle_product_active(
    product_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> ProductResponseDTO:
    """切換商品的上架/下架狀態"""
    try:
        use_case = ToggleProductActiveUseCase(SqlAlchemyProductRepository(db))
        product = await use_case.execute(product_id)
        return ProductResponseDTO.model_validate(product)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post(
    "/{product_id}/adjust-stock",
    response_model=ProductResponseDTO,
    summary="調整商品庫存",
    description="調整商品庫存數量"
)
async def adjust_product_stock(
    product_id: UUID,
    data: ProductStockAdjustDTO,
    db: AsyncSession = Depends(get_db)
) -> ProductResponseDTO:
    """
    調整商品庫存

    - **quantity_change**: 庫存變化量 (正數增加，負數減少)
    - **reason**: 調整原因 (選填)
    """
    try:
        use_case = AdjustProductStockUseCase(SqlAlchemyProductRepository(db))
        product = await use_case.execute(product_id, data.quantity_change)
        return ProductResponseDTO.model_validate(product)
    except ValueError as e:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "不存在" in str(e)
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=status_code, detail=str(e))

