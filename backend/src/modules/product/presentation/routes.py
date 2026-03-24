"""
Product API Routes

定義 Product 模組的 HTTP API 端點
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from typing import List, Optional
from uuid import UUID

from infrastructure.database import get_db, get_redis_optional
from infrastructure.product_cache_service import ProductCacheService
from infrastructure.stock_redis_service import StockRedisService
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
from modules.product.infrastructure.category_repository import SqlAlchemyCategoryRepository
from modules.product.application.dtos import (
    ProductCreateDTO,
    ProductUpdateDTO,
    ProductResponseDTO,
    ProductListResponseDTO,
    ProductStockAdjustDTO,
    CategoryResponseDTO,
)


router = APIRouter(prefix="/products", tags=["Products"])


# ==================== 分類操作 ====================

@router.get(
    "/categories",
    response_model=List[CategoryResponseDTO],
    summary="列出所有分類",
    description="列出所有可用的商品分類"
)
async def list_categories(
    db: AsyncSession = Depends(get_db)
) -> List[CategoryResponseDTO]:
    """列出所有分類"""
    repo = SqlAlchemyCategoryRepository(db)
    categories = await repo.list()
    return [CategoryResponseDTO(id=c.id, name=c.name, slug=c.slug) for c in categories]


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
    db: AsyncSession = Depends(get_db),
    redis: Optional[Redis] = Depends(get_redis_optional),
) -> ProductResponseDTO:
    """取得指定 UUID 的商品詳細資訊"""
    cache_service = ProductCacheService(redis)

    # Cache-Aside: 先查快取
    cached = await cache_service.get_product_detail(product_id)
    if cached is not None:
        return ProductResponseDTO.model_validate(cached)

    try:
        use_case = GetProductUseCase(SqlAlchemyProductRepository(db))
        product = await use_case.execute(product_id)
        dto = ProductResponseDTO.model_validate(product)

        # 回寫快取
        await cache_service.set_product_detail(product_id, dto.model_dump(mode="json"))

        return dto
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "",
    response_model=ProductListResponseDTO,
    summary="列出商品",
    description="取得商品清單，支援分頁與分類篩選"
)
async def list_products(
    skip: int = Query(default=0, ge=0, description="略過的筆數"),
    limit: int = Query(default=100, ge=1, le=1000, description="取得的筆數上限"),
    category_id: Optional[int] = Query(default=None, description="分類 ID 篩選"),
    category_ids: Optional[List[int]] = Query(default=None, description="分類 ID 列表篩選"),
    is_active: Optional[bool] = Query(default=None, description="篩選上架狀態"),
    db: AsyncSession = Depends(get_db),
    redis: Optional[Redis] = Depends(get_redis_optional),
) -> ProductListResponseDTO:
    """
    列出商品清單

    - **skip**: 略過的筆數
    - **limit**: 取得的筆數上限 (最大 1000)
    - **category_id**: 分類 ID 篩選
    - **category_ids**: 分類 ID 列表篩選
    - **is_active**: 篩選上架狀態 (null=全部, true=上架, false=下架)
    """
    cache_service = ProductCacheService(redis)
    cache_key = ProductCacheService.build_list_cache_key(
        skip=skip, limit=limit, category_id=category_id,
        category_ids=category_ids, is_active=is_active,
    )

    # Cache-Aside: 先查快取
    cached = await cache_service.get_product_list(cache_key)
    if cached is not None:
        return ProductListResponseDTO.model_validate(cached)

    use_case = ListProductsUseCase(SqlAlchemyProductRepository(db))
    products, total = await use_case.execute(
        skip=skip,
        limit=limit,
        category_id=category_id,
        category_ids=category_ids,
        is_active=is_active
    )

    dto = ProductListResponseDTO(
        items=[ProductResponseDTO.model_validate(p) for p in products],
        total=total,
        skip=skip,
        limit=limit
    )

    # 回寫快取
    await cache_service.set_product_list(cache_key, dto.model_dump(mode="json"))

    return dto



@router.put(
    "/{product_id}",
    response_model=ProductResponseDTO,
    summary="更新商品",
    description="更新商品資訊（部分更新）"
)
async def update_product(
    product_id: UUID,
    data: ProductUpdateDTO,
    db: AsyncSession = Depends(get_db),
    redis: Optional[Redis] = Depends(get_redis_optional),
) -> ProductResponseDTO:
    """更新商品資訊 (部分更新)"""
    try:
        use_case = UpdateProductUseCase(SqlAlchemyProductRepository(db))
        product = await use_case.execute(product_id, data)

        cache_service = ProductCacheService(redis)
        db.info["after_commit"].append(
            lambda: cache_service.invalidate_product_detail(product_id)
        )
        db.info["after_commit"].append(cache_service.invalidate_all_product_lists)

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
    db: AsyncSession = Depends(get_db),
    redis: Optional[Redis] = Depends(get_redis_optional),
) -> None:
    """刪除指定 UUID 的商品"""
    try:
        use_case = DeleteProductUseCase(SqlAlchemyProductRepository(db))
        await use_case.execute(product_id)

        cache_service = ProductCacheService(redis)
        db.info["after_commit"].append(
            lambda: cache_service.invalidate_product_detail(product_id)
        )
        db.info["after_commit"].append(cache_service.invalidate_all_product_lists)
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
    db: AsyncSession = Depends(get_db),
    redis: Optional[Redis] = Depends(get_redis_optional),
) -> ProductResponseDTO:
    """切換商品的上架/下架狀態"""
    try:
        use_case = ToggleProductActiveUseCase(SqlAlchemyProductRepository(db))
        product = await use_case.execute(product_id)

        cache_service = ProductCacheService(redis)
        db.info["after_commit"].append(
            lambda: cache_service.invalidate_product_detail(product_id)
        )
        db.info["after_commit"].append(cache_service.invalidate_all_product_lists)

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
    db: AsyncSession = Depends(get_db),
    redis: Optional[Redis] = Depends(get_redis_optional),
) -> ProductResponseDTO:
    """
    調整商品庫存

    - **quantity_change**: 庫存變化量 (正數增加，負數減少)
    - **reason**: 調整原因 (選填)
    """
    try:
        stock_service = StockRedisService(redis, db)
        use_case = AdjustProductStockUseCase(SqlAlchemyProductRepository(db), stock_service)
        product = await use_case.execute(product_id, data.quantity_change)

        cache_service = ProductCacheService(redis)
        db.info["after_commit"].append(
            lambda: cache_service.invalidate_product_detail(product_id)
        )
        db.info["after_commit"].append(cache_service.invalidate_all_product_lists)

        return ProductResponseDTO.model_validate(product)
    except ValueError as e:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "不存在" in str(e)
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=status_code, detail=str(e))

