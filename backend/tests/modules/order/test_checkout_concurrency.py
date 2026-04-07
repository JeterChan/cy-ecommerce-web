import pytest
import pytest_asyncio
import uuid
import os
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from redis.asyncio import Redis
from sqlalchemy import select

from main import app
from infrastructure.database import Base, get_db, get_redis
from modules.product.infrastructure.models import ProductModel
from modules.auth.infrastructure.models import UserModel
from modules.cart.infrastructure.repositories.hybrid_repository import (
    HybridCartRepository,
)
from core.security import create_access_token

# Test Database Configuration
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://jeter:Oyn0BkxSj5TLxP@db:5432/test_ecommerce_db",
)
TEST_REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://redis:6379/1")

# 建立全域引擎，使用更大的 pool 並允許 overflow 以支援併發
engine = create_async_engine(TEST_DATABASE_URL, pool_size=20, max_overflow=10)
TestingSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture
async def async_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_redis():
    redis = Redis.from_url(TEST_REDIS_URL, decode_responses=True)
    yield redis
    await redis.flushdb()
    await redis.aclose()


@pytest.mark.asyncio
async def test_checkout_concurrency_pessimistic_lock(
    async_db: AsyncSession, async_redis: Redis
):
    # 1. 準備商品庫存 5
    product = ProductModel(
        name="Hot Product", price=100.0, stock_quantity=5, is_active=True
    )
    async_db.add(product)
    await async_db.commit()
    product_id = product.id

    # 2. 準備 10 個使用者並分配 Token
    num_users = 10
    users_data = []
    for i in range(num_users):
        u = UserModel(
            email=f"user_{i}_{uuid.uuid4().hex[:4]}@example.com",
            username=f"user_{i}_{uuid.uuid4().hex[:4]}",
            password_hash="...",
            is_active=True,
        )
        async_db.add(u)
        users_data.append(u)
    await async_db.commit()

    # 為每個使用者準備購物車
    for u in users_data:
        token = create_access_token(data={"sub": u.email})
        u.test_token = token
        cart_repo = HybridCartRepository(async_redis, async_db)
        await cart_repo.add_item(str(u.id), product_id, 1)

    # 3. 定義併發請求任務，並 Override dependencies
    # 這裡我們需要確保每次呼叫 get_db 都得到一個新的、獨立的 session
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
            # 我們不手動 commit，因為 UseCase 內有 async with self.db.begin()

    async def override_get_redis():
        redis = Redis.from_url(TEST_REDIS_URL, decode_responses=True)
        yield redis
        await redis.aclose()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    async def do_checkout(user_obj):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            headers = {"Authorization": f"Bearer {user_obj.test_token}"}
            data = {
                "recipient_name": "Concurrency Test",
                "recipient_phone": "0900000000",
                "shipping_address": "Test Address",
                "payment_method": "COD",
            }
            return await ac.post("/api/v1/orders/checkout", json=data, headers=headers)

    # 4. 啟動併發請求
    results = await asyncio.gather(*[do_checkout(u) for u in users_data])

    app.dependency_overrides.clear()

    # 5. 驗證結果
    success_count = sum(1 for r in results if r.status_code == 201)
    fail_count = sum(1 for r in results if r.status_code == 400)

    print(f"Success: {success_count}, Fail: {fail_count}")

    # 由於鎖定應該生效，後續的請求應該在鎖釋放後發現庫存不足
    assert success_count == 5
    assert fail_count == 5

    # 6. 驗證最終庫存
    # 重新獲取一個 session 查詢
    async with TestingSessionLocal() as session:
        res_p = await session.execute(
            select(ProductModel).where(ProductModel.id == product_id)
        )
        p_after = res_p.scalar_one()
        assert p_after.stock_quantity == 0
