"""
seed_categories.py

Seed 初始分類資料至 categories 資料表
執行方式：cd backend && python -m scripts.seed_categories
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from infrastructure.config import settings
from modules.product.infrastructure.models import CategoryModel

INITIAL_CATEGORIES = [
    {"name": "服飾", "slug": "clothing"},
    {"name": "電子", "slug": "electronics"},
    {"name": "居家", "slug": "home"},
    {"name": "食品", "slug": "food"},
    {"name": "美妝", "slug": "beauty"},
    {"name": "運動", "slug": "sports"},
    {"name": "書籍", "slug": "books"},
    {"name": "玩具", "slug": "toys"},
    {"name": "汽車配件", "slug": "automotive"},
    {"name": "其他", "slug": "others"},
]


async def seed_categories():
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        created_count = 0
        skipped_count = 0

        for cat_data in INITIAL_CATEGORIES:
            result = await session.execute(
                select(CategoryModel).where(CategoryModel.slug == cat_data["slug"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  [SKIP] 分類已存在: {cat_data['name']} ({cat_data['slug']})")
                skipped_count += 1
            else:
                category = CategoryModel(name=cat_data["name"], slug=cat_data["slug"])
                session.add(category)
                print(f"  [ADD]  建立分類: {cat_data['name']} ({cat_data['slug']})")
                created_count += 1

        await session.commit()

    print(f"\n完成！新增 {created_count} 個分類，略過 {skipped_count} 個已存在的分類。")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_categories())
