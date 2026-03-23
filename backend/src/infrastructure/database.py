from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator, TYPE_CHECKING
from infrastructure.config import settings

if TYPE_CHECKING:
    import redis.asyncio as aioredis

engine = create_async_engine(
    settings.database_url,
    echo=False,  # 關閉 SQL log,避免 I/O 開銷
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

# Redis config
redis_client: "aioredis.Redis | None" = None

async def init_redis() -> None:
    import redis.asyncio as aioredis
    global redis_client

    # 使用 settings.redis_url (已包含密碼與完整連線資訊)
    redis_client = await aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=50,
        socket_connect_timeout=5,
        socket_keepalive=True,
    )

    print("Redis connection established successfully")

async def close_redis() -> None:
    """
        Close Redis connection pool and release all resources.

        Should be called during application shutdown to ensure graceful cleanup.
        Closes all active connections in the pool.
    """
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
        print("Redis connection closed successfully")

async def get_redis() -> "aioredis.Redis":
    if redis_client is None:
        raise RuntimeError(
            "Redis client is not initialized. Ensure init_redis() is called during application startup before using get_redis()."
        )
    return redis_client # 回傳共用實例

async def drop_all() -> None:
    """
    Drop all tables declared on Base's metadata from the connected database.
    
    This permanently removes all database tables. Intended for development use only.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, checkfirst=True)
    print("All database tables dropped successfully")

async def recreate_all() -> None:
    """
    Recreate all database tables by dropping them and then creating them from the ORM metadata.
    
    This is a destructive operation that removes all data; intended for development use only.
    """
    await drop_all()
    await init_db()
    print("Database tables recreated successfully")