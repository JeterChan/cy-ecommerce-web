import pytest
import uuid
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from contextlib import asynccontextmanager
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
import pytest_asyncio
import os
from redis.asyncio import Redis

from infrastructure.database import Base
from infrastructure.redis import redis_manager
from modules.cart.infrastructure.repositories.hybrid_repository import HybridCartRepository
from modules.cart.infrastructure.tasks import sync_member_cart_task, sync_member_cart_logic
from modules.cart.infrastructure.models import CartItemModel, CartModel
from modules.product.infrastructure.models import ProductModel
from modules.auth.infrastructure.models import UserModel
from decimal import Decimal

# ──────────────────────────────────────────────
# Test Database Setup
# ──────────────────────────────────────────────

TEST_DATABASE_URL = (
    "postgresql+asyncpg://"
    f"{os.getenv('TEST_DB_USER', 'user')}:{os.getenv('TEST_DB_PASSWORD', 'password')}"
    f"@{os.getenv('TEST_DB_HOST', 'localhost')}:{os.getenv('TEST_DB_PORT', '5432')}"
    f"/{os.getenv('TEST_DB_NAME', 'test_ecommerce_db')}"
)

@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """每个测试函式前後 drop/create 全部資料表，確保測試隔離。"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine) -> AsyncSession:
    """提供測試用 AsyncSession，測試後 rollback 未提交的殘餘變更。"""
    factory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture(scope="function")
async def redis_client() -> Redis:
    """連接 Redis DB 15，測試前後清空，確保測試隔離。"""
    client = await Redis.from_url(
        f"redis://{os.getenv('TEST_DB_HOST', 'localhost')}:6379/15",
        encoding="utf-8",
        decode_responses=True,
    )
    await client.flushdb()
    yield client
    await client.flushdb()
    await client.aclose()


@pytest.mark.asyncio
@pytest.mark.integration
class TestCartSyncTaskIntegration:
    """測試購物車非同步同步流程 (API -> Redis -> Task -> DB)"""

    async def test_hybrid_repo_triggers_celery_task(self, async_session: AsyncSession, redis_client: Redis):
        """測試 HybridRepository 是否正確觸發 Celery 任務"""
        # Arrange
        user_id = str(uuid.uuid4())
        product_id = uuid.uuid4()
        
        # 使用測試 Redis Client
        repo = HybridCartRepository(redis_client, async_session)
        
        # Mock Celery apply_async
        with patch("modules.cart.infrastructure.tasks.sync_member_cart_task.apply_async") as mock_apply:
            # Act
            await repo.add_item(user_id, product_id, 2)
            
            # Assert
            mock_apply.assert_called_once()
            # apply_async is called with keyword args: args=[...], queue=...
            _, kwargs = mock_apply.call_args
            assert kwargs["args"] == [user_id]
            assert kwargs["queue"] == "cart_sync_queue"

    async def test_sync_task_persists_to_postgresql(self, async_session: AsyncSession, redis_client: Redis):
        """測試同步任務是否能將 Redis 數據正確寫入 PostgreSQL"""
        # Arrange
        user_uuid_obj = uuid.uuid4()
        user_id = str(user_uuid_obj)
        product_id = uuid.uuid4()
        quantity = 5
        
        # 0. 建立 User (避免 Foreign Key Error)
        user = UserModel(
            id=user_uuid_obj,
            email=f"test_{user_id}@example.com",
            username=f"user_{user_id}",
            password_hash="hashed_secret",
            is_active=True,
            is_verified=True
        )
        async_session.add(user)
        await async_session.commit()
        
        # 1. 直接寫入 Redis
        from modules.cart.infrastructure.repositories.redis_repository import RedisCartRepository
        redis_repo = RedisCartRepository(redis_client)
        await redis_repo.add_item(user_id, product_id, quantity)
        
        # 2. 準備產品 (避免 FK 錯誤，如果有的話)
        product = ProductModel(
            id=product_id,
            name="Sync Test Product",
            price=Decimal("99.99"),
            stock_quantity=100
        )
        async_session.add(product)
        await async_session.commit()
        
        # 3. 執行同步邏輯 (直接呼叫 async function)
        # 需 Mock settings 與 redis_manager
        with patch("modules.cart.infrastructure.tasks.settings") as mock_settings, \
             patch("modules.cart.infrastructure.tasks.redis_manager") as mock_rm:
            
            # 設定 Test DB
            mock_settings.database_url = TEST_DATABASE_URL
            
            # 設定 Mock Redis Manager 行為
            mock_rm.client = redis_client
            mock_rm.connect = AsyncMock()
            
            @asynccontextmanager
            async def mock_lock(*args, **kwargs):
                yield True
            mock_rm.distributed_lock = mock_lock

            await sync_member_cart_logic(user_id)
        
        # 4. 驗證資料庫
        async with async_session.begin():
            result = await async_session.execute(
                text("SELECT ci.quantity FROM cart_items ci JOIN carts c ON ci.cart_id = c.id WHERE c.user_id = :uid"),
                {"uid": uuid.UUID(user_id)}
            )
            db_quantity = result.scalar()
            
            assert db_quantity == quantity

    async def test_sync_task_handles_deletions(self, async_session: AsyncSession, redis_client: Redis):
        """測試同步任務是否能清理已從 Redis 移除的項目"""
        # Arrange
        user_uuid_obj = uuid.uuid4()
        user_id = str(user_uuid_obj)
        p1 = uuid.uuid4()
        p2 = uuid.uuid4()
        
        # 0. 建立 User
        user = UserModel(
            id=user_uuid_obj,
            email=f"test_{user_id}@example.com",
            username=f"user_{user_id}",
            password_hash="hashed_secret",
            is_active=True,
            is_verified=True
        )
        async_session.add(user)
        await async_session.commit()
        
        # 1. 初始狀態：Redis 有 p1, p2
        from modules.cart.infrastructure.repositories.redis_repository import RedisCartRepository
        redis_repo = RedisCartRepository(redis_client)
        await redis_repo.add_item(user_id, p1, 1)
        await redis_repo.add_item(user_id, p2, 1)
        
        # 準備產品 (避免 FK)
        async_session.add_all([
            ProductModel(id=p1, name="P1", price=10, stock_quantity=10),
            ProductModel(id=p2, name="P2", price=10, stock_quantity=10)
        ])
        await async_session.commit()
        
        # Mock settings & redis_manager context
        with patch("modules.cart.infrastructure.tasks.settings") as mock_settings, \
             patch("modules.cart.infrastructure.tasks.redis_manager") as mock_rm:
            
            mock_settings.database_url = TEST_DATABASE_URL
            mock_rm.client = redis_client
            mock_rm.connect = AsyncMock()
            @asynccontextmanager
            async def mock_lock(*args, **kwargs):
                yield True
            mock_rm.distributed_lock = mock_lock

            # 2. 同步到 DB
            await sync_member_cart_logic(user_id)
            
            # 3. 從 Redis 移除 p1
            await redis_repo.remove_item(user_id, p1)
            
            # 4. 再次同步
            await sync_member_cart_logic(user_id)
            
            # 5. 驗證 DB 只有 p2
            result = await async_session.execute(
                text("SELECT COUNT(*) FROM cart_items ci JOIN carts c ON ci.cart_id = c.id WHERE c.user_id = :uid"),
                {"uid": uuid.UUID(user_id)}
            )
            count = result.scalar()
            assert count == 1

    async def test_sync_task_retries_on_lock_failure(self):
        """測試當無法取得鎖時，是否會觸發 Retry"""
        user_id = str(uuid.uuid4())
        mock_task = MagicMock()
        mock_task.retry.side_effect = Exception("Retry triggered") # Simulate retry exception
        
        with patch("modules.cart.infrastructure.tasks.settings") as mock_settings, \
             patch("modules.cart.infrastructure.tasks.redis_manager") as mock_rm:
             
             mock_settings.database_url = TEST_DATABASE_URL
             mock_rm.connect = AsyncMock()
             
             # Mock lock to fail acquisition
             @asynccontextmanager
             async def mock_lock(*args, **kwargs):
                 yield False # Not acquired
             mock_rm.distributed_lock = mock_lock
             
             # Act & Assert
             with pytest.raises(Exception, match="Retry triggered"):
                 await sync_member_cart_logic(user_id, task_instance=mock_task)
             
             mock_task.retry.assert_called_once_with(countdown=1)
