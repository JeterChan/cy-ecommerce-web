import pytest
import pytest_asyncio
import uuid
import os
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

from main import app
from infrastructure.database import Base, get_db
from modules.auth.infrastructure.models import UserModel
from modules.order.infrastructure.models import OrderModel
from modules.order.domain.value_objects import OrderStatus
from core.security import create_access_token

# Test Database Configuration
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://jeter:Oyn0BkxSj5TLxP@db:5432/test_ecommerce_db",
)


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
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_admin_list_orders_success(
    async_client: AsyncClient, async_db: AsyncSession
):
    # 1. 準備測試資料：管理員與一般使用者
    admin_user = UserModel(
        email="admin@example.com",
        username="admin",
        password_hash="hashed_password",
        role="admin",
        is_active=True,
        is_verified=True,
    )
    user = UserModel(
        email="user@example.com",
        username="user",
        password_hash="hashed_password",
        role="user",
        is_active=True,
        is_verified=True,
    )
    async_db.add_all([admin_user, user])
    await async_db.flush()

    # 2. 建立一些訂單
    order1 = OrderModel(
        user_id=user.id,
        order_number="ORDER001",
        status=OrderStatus.PENDING,
        total_amount=100.0,
        shipping_fee=60.0,
        recipient_name="Recipient 1",
        recipient_phone="0912345678",
        shipping_address="Address 1",
        payment_method="COD",
        status_updated_at=None,
    )
    order2 = OrderModel(
        user_id=user.id,
        order_number="ORDER002",
        status=OrderStatus.PAID,
        total_amount=200.0,
        shipping_fee=60.0,
        recipient_name="Recipient 2",
        recipient_phone="0912345678",
        shipping_address="Address 2",
        payment_method="COD",
        status_updated_at=None,
    )
    async_db.add_all([order1, order2])
    await async_db.commit()

    # 3. 登入管理員並獲取 Token
    access_token = create_access_token(data={"sub": admin_user.email})
    headers = {"Authorization": f"Bearer {access_token}"}

    # 4. 執行管理員列表 API
    async def override_get_db():
        yield async_db

    app.dependency_overrides[get_db] = override_get_db

    response = await async_client.get("/api/v1/admin/orders", headers=headers)

    # 清除 override
    app.dependency_overrides.clear()

    # 5. 驗證結果
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["orders"]) == 2
    assert data["orders"][0]["order_number"] in ["ORDER001", "ORDER002"]


@pytest.mark.asyncio
async def test_admin_list_orders_forbidden_for_user(
    async_client: AsyncClient, async_db: AsyncSession
):
    # 1. 準備一般使用者
    user = UserModel(
        email="user_forbidden@example.com",
        username="user_forbidden",
        password_hash="hashed_password",
        role="user",
        is_active=True,
        is_verified=True,
    )
    async_db.add(user)
    await async_db.commit()

    # 2. 登入一般使用者
    access_token = create_access_token(data={"sub": user.email})
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. 嘗試存取管理員 API
    async def override_get_db():
        yield async_db

    app.dependency_overrides[get_db] = override_get_db

    response = await async_client.get("/api/v1/admin/orders", headers=headers)
    app.dependency_overrides.clear()

    # 4. 驗證被拒絕
    assert response.status_code == 403
    assert "權限不足" in response.json()["detail"]


@pytest.mark.asyncio
async def test_admin_update_order_success(
    async_client: AsyncClient, async_db: AsyncSession
):
    # 1. 準備資料
    admin_user = UserModel(
        email="admin_update@example.com",
        username="admin_update",
        password_hash="hashed_password",
        role="admin",
        is_active=True,
        is_verified=True,
    )
    async_db.add(admin_user)
    await async_db.flush()

    order = OrderModel(
        user_id=uuid.uuid4(),
        order_number="UPDATE001",
        status=OrderStatus.PENDING,
        total_amount=500.0,
        shipping_fee=0.0,
        recipient_name="Recipient",
        recipient_phone="0912345678",
        shipping_address="Address",
        payment_method="COD",
    )
    async_db.add(order)
    await async_db.commit()
    await async_db.refresh(order)

    # 2. 登入管理員
    access_token = create_access_token(data={"sub": admin_user.email})
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. 執行更新
    async def override_get_db():
        yield async_db

    app.dependency_overrides[get_db] = override_get_db

    update_data = {
        "status": "SHIPPED",
        "admin_note": "This order is now shipped by admin.",
    }

    response = await async_client.patch(
        f"/api/v1/admin/orders/{order.id}", json=update_data, headers=headers
    )
    app.dependency_overrides.clear()

    # 4. 驗證結果
    if response.status_code != 200:
        print(f"Error detail: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SHIPPED"
    assert data["admin_note"] == "This order is now shipped by admin."
    assert data["status_updated_at"] is not None

    # 5. 驗證資料庫
    res = await async_db.execute(select(OrderModel).where(OrderModel.id == order.id))
    db_order = res.scalar_one()
    assert db_order.status == OrderStatus.SHIPPED
    assert db_order.admin_note == "This order is now shipped by admin."
    assert db_order.status_updated_at is not None
