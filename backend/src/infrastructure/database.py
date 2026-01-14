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
    """
    Provide an AsyncSession for a transactional unit of work; commit is attempted after the caller finishes and the transaction is rolled back if an exception occurs.
    
    Returns:
        session (AsyncSession): The database session bound to a transaction; the transaction is committed after use, or rolled back if an exception is raised.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# for dev
async def init_db() -> None:
    """
    Create all database tables declared on the module's Declarative Base using the configured engine.
    
    This establishes the schema defined by Base.metadata against the database and prints a confirmation message upon success.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully")

async def drop_all() -> None:
    """
    Drop all tables declared on Base's metadata from the connected database.
    
    This permanently removes all database tables. Intended for development use only.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("All database tables dropped successfully")

async def recreate_all() -> None:
    """
    Recreate all database tables by dropping them and then creating them from the ORM metadata.
    
    This is a destructive operation that removes all data; intended for development use only.
    """
    await drop_all()
    await init_db()
    print("Database tables recreated successfully")