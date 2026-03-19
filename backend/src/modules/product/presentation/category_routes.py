"""
Admin Category API Routes

管理員專用分類管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List

from infrastructure.database import get_db
from modules.auth.presentation.routes import require_admin
from modules.auth.domain.entities import UserEntity
from modules.product.application.dtos import CategoryResponseDTO, CategoryCreateDTO, CategoryUpdateDTO
from modules.product.domain.entities import Category
from modules.product.infrastructure.category_repository import SqlAlchemyCategoryRepository

router = APIRouter(prefix="/admin/categories", tags=["Admin Categories"])


@router.get(
    "",
    response_model=List[CategoryResponseDTO],
    summary="取得所有分類 (管理員)"
)
async def admin_list_categories(
    db: AsyncSession = Depends(get_db),
    admin: UserEntity = Depends(require_admin)
) -> List[CategoryResponseDTO]:
    repo = SqlAlchemyCategoryRepository(db)
    categories = await repo.list()
    return [CategoryResponseDTO(id=c.id, name=c.name, slug=c.slug) for c in categories]


@router.post(
    "",
    response_model=CategoryResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="新增分類 (管理員)"
)
async def admin_create_category(
    data: CategoryCreateDTO,
    db: AsyncSession = Depends(get_db),
    admin: UserEntity = Depends(require_admin)
) -> CategoryResponseDTO:
    repo = SqlAlchemyCategoryRepository(db)
    try:
        category = Category(id=None, name=data.name, slug=data.slug)
        category.validate()
        if await repo.get_by_slug(data.slug):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="分類 Slug 已存在")
        if await repo.get_by_name(data.name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="分類名稱已存在")
        created = await repo.create(category)
        return CategoryResponseDTO(id=created.id, name=created.name, slug=created.slug)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="分類名稱或 slug 已存在")


@router.patch(
    "/{category_id}",
    response_model=CategoryResponseDTO,
    summary="更新分類 (管理員)"
)
async def admin_update_category(
    category_id: int,
    data: CategoryUpdateDTO,
    db: AsyncSession = Depends(get_db),
    admin: UserEntity = Depends(require_admin)
) -> CategoryResponseDTO:
    repo = SqlAlchemyCategoryRepository(db)
    try:
        existing = await repo.get_by_id(category_id)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分類不存在")
        merged_name = data.name if data.name is not None else existing.name
        merged_slug = data.slug if data.slug is not None else existing.slug
        candidate = Category(id=existing.id, name=merged_name, slug=merged_slug)
        candidate.validate()
        updated = await repo.update(category_id, data.name, data.slug)
        return CategoryResponseDTO(id=updated.id, name=updated.name, slug=updated.slug)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="分類名稱或 slug 已存在")


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="刪除分類 (管理員)"
)
async def admin_delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    admin: UserEntity = Depends(require_admin)
) -> None:
    repo = SqlAlchemyCategoryRepository(db)
    deleted = await repo.delete(category_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分類不存在")
