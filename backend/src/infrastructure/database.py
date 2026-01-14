from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from infrastructure.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=True, # prod 要關閉
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True, # 推薦開啟：自動偵測斷線並重連
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# for dev
async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully")

async def drop_all() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("All database tables dropped successfully")

async def recreate_all() -> None:
    """開發環境重建所有資料表（先刪除再建立）"""
    await drop_all()
    await init_db()
    print("Database tables recreated successfully")