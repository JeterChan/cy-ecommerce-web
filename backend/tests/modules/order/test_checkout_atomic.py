import pytest
import pytest_asyncio
import uuid
import os
from decimal import Decimal
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from redis.asyncio import Redis

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


@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def async_redis():
    redis = Redis.from_url(TEST_REDIS_URL, decode_responses=True)
    yield redis
    await redis.flushdb()
    await redis.aclose()


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_checkout_success(
    async_client: AsyncClient, async_db: AsyncSession, async_redis: Redis
):
    # 1. 準備測試資料：使用者與商品
    unique_suffix = uuid.uuid4().hex[:6]
    test_user = UserModel(
        email=f"test_{unique_suffix}@example.com",
        username=f"testuser_{unique_suffix}",
        password_hash="hashed_password",
        is_active=True,
    )
    async_db.add(test_user)
    await async_db.flush()
    await async_db.refresh(test_user)

    product1 = ProductModel(
        name="Test Product 1", price=100.0, stock_quantity=10, is_active=True
    )
    product2 = ProductModel(
        name="Test Product 2", price=200.0, stock_quantity=5, is_active=True
    )
    async_db.add_all([product1, product2])
    await async_db.commit()

    # 2. 登入並取得 Token
    access_token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. 準備購物車資料
    cart_repo = HybridCartRepository(async_redis, async_db)
    await cart_repo.add_item(str(test_user.id), product1.id, 2)
    await cart_repo.add_item(str(test_user.id), product2.id, 1)

    # 4. 執行結帳 API - Override dependencies
    async def override_get_db():
        yield async_db

    async def override_get_redis():
        yield async_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    checkout_data = {
        "recipient_name": "Test Recipient",
        "recipient_phone": "0912345678",
        "shipping_address": "Test Address 123",
        "payment_method": "COD",
    }

    response = await async_client.post(
        "/api/v1/orders/checkout", json=checkout_data, headers=headers
    )

    # 清除 override
    app.dependency_overrides.clear()

    # 5. 驗證結果
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "PENDING"
    assert float(data["total_amount"]) == 400.0  # (100*2) + (200*1)

    # 6. 驗證庫存已扣除
    from sqlalchemy import select

    res1 = await async_db.execute(
        select(ProductModel).where(ProductModel.id == product1.id)
    )
    p1_after = res1.scalar_one()
    assert p1_after.stock_quantity == 8

    res2 = await async_db.execute(
        select(ProductModel).where(ProductModel.id == product2.id)
    )
    p2_after = res2.scalar_one()
    assert p2_after.stock_quantity == 4

    # 7. 驗證 Redis 購物車已清空
    cart_after = await cart_repo.get_cart(str(test_user.id))
    assert len(cart_after) == 0
