"""
信箱驗證流程的整合測試
測試範圍：註冊 -> 生成 Token -> 嘗試驗證前登入 -> 驗證 -> 驗證後登入
"""

import pytest
import pytest_asyncio
from unittest.mock import patch
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from redis.asyncio import Redis
import os

from infrastructure.database import Base
from modules.auth.application.use_cases.register import RegisterUserUseCase
from modules.auth.application.use_cases.login import LoginUserUseCase
from modules.auth.application.use_cases.verify_email import VerifyEmailUseCase
from modules.auth.application.dtos import RegisterRequestDTO, LoginRequestDTO
from modules.auth.infrastructure.repository import UserRepository
from modules.auth.infrastructure.password_hasher import BcryptPasswordHasher
from infrastructure.redis.token_manager import RedisTokenManager
from core.exceptions import InvalidCredentialsError

# Test Database/Redis Configuration
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/test_ecommerce_db",
)
TEST_REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://localhost:6379/1")


@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        yield session
        await session.rollback()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def redis_client():
    client = Redis.from_url(TEST_REDIS_URL)
    await client.flushdb()
    yield client
    await client.aclose()


@pytest.mark.asyncio
async def test_verification_flow_integration(async_session, redis_client):
    # Arrange
    user_repo = UserRepository(async_session)
    token_manager = RedisTokenManager(redis_client)

    # Mock Celery delay to avoid real email sending
    with patch(
        "modules.auth.application.use_cases.register.send_registration_verification"
    ) as mock_email_task:
        mock_email_task.delay = mock_email_task
        register_use_case = RegisterUserUseCase(user_repo, token_manager)
        login_use_case = LoginUserUseCase(user_repo, BcryptPasswordHasher())
        verify_use_case = VerifyEmailUseCase(user_repo, token_manager)

        email = "verify_test@example.com"
        password = "Password123!"
        username = "verify_user"

        # 1. 註冊
        reg_input = RegisterRequestDTO(
            username=username, email=email, password=password
        )
        reg_output = await register_use_case.execute(reg_input)

        assert reg_output.email == email
        mock_email_task.assert_called_once()

        # 從 Redis 取得 Token (模擬使用者從信件點擊)
        # 注意：我們需要知道 token 是什麼。在測試中我們可以掃描 Redis
        keys = await redis_client.keys("auth:verify:*")
        assert len(keys) == 1
        token = keys[0].decode().split(":")[-1]

        # 2. 嘗試在驗證前登入 -> 應失敗
        login_input = LoginRequestDTO(email=email, password=password)
        with pytest.raises(InvalidCredentialsError) as exc:
            await login_use_case.execute(login_input)
        assert "請先完成信箱驗證" in str(exc.value)

        # 3. 呼叫驗證 Use Case
        verify_result = await verify_use_case.execute(token)
        assert verify_result is True

        # 4. 驗證後登入 -> 應成功
        login_output = await login_use_case.execute(login_input)
        assert login_output.access_token is not None
        assert login_output.user.email == email

        # 5. 再次使用同個 Token 驗證 -> 應失敗 (單次使用)
        with pytest.raises(ValueError) as exc:
            await verify_use_case.execute(token)
        assert "無效或過期" in str(exc.value)
