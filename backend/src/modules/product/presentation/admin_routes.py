"""
Admin Product API Routes

定義管理員專用的商品管理 HTTP API 端點
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from typing import List, Optional
from uuid import UUID, uuid4
import math

from infrastructure.database import get_db, get_redis
from infrastructure.stock_redis_service import StockRedisService
from modules.auth.presentation.routes import require_admin
from modules.auth.domain.entities import UserEntity
from modules.product.application.use_cases import (
    CreateProductUseCase,
    UpdateProductUseCase,
    DeleteProductUseCase,
    ListProductsAdminUseCase,
)
from modules.product.application.dtos import (
    ProductCreateDTO,
    ProductUpdateDTO,
    ProductResponseDTO,
    ProductListResponseDTO,
    ImagePresignRequest,
)
from infrastructure.s3 import s3_client

router = APIRouter(prefix="/admin/products", tags=["Admin Products"])

@router.get(
    "",
    summary="獲取商品列表 (管理員，支援搜尋/篩選/排序/分頁)"
)
async def admin_list_products(
    page: int = Query(default=1, ge=1, description="頁碼"),
    limit: int = Query(default=10, ge=1, le=100, description="每頁筆數"),
    search: Optional[str] = Query(default=None, description="搜尋商品名稱"),
    category_id: Optional[int] = Query(default=None, description="分類 ID 篩選"),
    sort: str = Query(default="created_desc", description="排序：created_desc 或 created_asc"),
    db: AsyncSession = Depends(get_db),
    admin: UserEntity = Depends(require_admin)
) -> dict:
    """獲取商品完整列表，包含下架商品，支援搜尋、分類篩選、排序與分頁"""
    from modules.product.infrastructure.repository import SqlAlchemyProductRepository
    use_case = ListProductsAdminUseCase(SqlAlchemyProductRepository(db))
    products, total = await use_case.execute(
        page=page,
        limit=limit,
        search=search,
        category_id=category_id,
        sort=sort,
    )
    pages = math.ceil(total / limit) if total > 0 else 1
    return {
        "products": [ProductResponseDTO.model_validate(p).model_dump() for p in products],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
    }

@router.post(
    "/images/presign",
    summary="獲取 S3 預簽名 URL (管理員)"
)
async def get_image_presigned_url(
    data: ImagePresignRequest,
    admin: UserEntity = Depends(require_admin)
) -> dict:
    """獲取上傳圖片用的預簽名 URL"""
    file_ext = data.filename.split(".")[-1] if "." in data.filename else "jpg"
    object_name = f"products/temp/{uuid4()}.{file_ext}"
    
    upload_url = s3_client.generate_presigned_url(
        object_name=object_name,
        content_type=data.content_type
    )
    
    if not upload_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="無法連接至雲端存儲服務"
        )
        
    return {
        "upload_url": upload_url,
        "image_url": f"https://{s3_client.bucket_name}.s3.{s3_client.region}.amazonaws.com/{object_name}"
    }

@router.post(
    "",
    response_model=ProductResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="建立商品 (管理員)"
)
async def admin_create_product(
    data: ProductCreateDTO,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    admin: UserEntity = Depends(require_admin)
) -> ProductResponseDTO:
    """建立新商品，僅限管理員權限"""
    try:
        from modules.product.infrastructure.repository import SqlAlchemyProductRepository
        stock_service = StockRedisService(redis, db)
        use_case = CreateProductUseCase(SqlAlchemyProductRepository(db), stock_service)
        product = await use_case.execute(data)
        return ProductResponseDTO.model_validate(product)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put(
    "/{product_id}",
    response_model=ProductResponseDTO,
    summary="更新商品 (管理員)"
)
async def admin_update_product(
    product_id: UUID,
    data: ProductUpdateDTO,
    db: AsyncSession = Depends(get_db),
    admin: UserEntity = Depends(require_admin)
) -> ProductResponseDTO:
    """更新商品資訊，僅限管理員權限"""
    try:
        from modules.product.infrastructure.repository import SqlAlchemyProductRepository
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
    summary="刪除商品 (管理員)"
)
async def admin_delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: UserEntity = Depends(require_admin)
) -> None:
    """刪除指定 UUID 的商品，僅限管理員權限"""
    try:
        from modules.product.infrastructure.repository import SqlAlchemyProductRepository
        use_case = DeleteProductUseCase(SqlAlchemyProductRepository(db))
        await use_case.execute(product_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
