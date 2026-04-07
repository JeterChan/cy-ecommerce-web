"""
密碼重設流程的整合測試
測試範圍：請求重設 -> 生成 Token -> 使用 Token 重設密碼 -> 以新密碼登入
"""

import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from redis.asyncio import Redis
import os

from src.infrastructure.database import Base
from src.modules.auth.use_cases.register import RegisterUserUseCase
from src.modules.auth.use_cases.login import LoginUserUseCase
from src.modules.auth.application.use_cases.forgot_password import ForgotPasswordUseCase
from src.modules.auth.application.use_cases.reset_password import ResetPasswordUseCase
from src.modules.auth.application.dtos import RegisterRequestDTO, LoginRequestDTO
from src.modules.auth.infrastructure.repositories.user_repository import UserRepository
from src.infrastructure.redis.token_manager import RedisTokenManager
from src.core.exceptions import InvalidCredentialsError

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
    await client.close()


@pytest.mark.asyncio
async def test_password_reset_flow_integration(async_session, redis_client):
    # Arrange
    user_repo = UserRepository(async_session)
    token_manager = RedisTokenManager(redis_client)

    # Mock Celery delay to avoid real email sending
    with patch(
        "src.modules.auth.use_cases.register.send_registration_verification.delay"
    ), patch(
        "src.modules.auth.application.use_cases.forgot_password.send_password_reset.delay"
    ) as mock_reset_task:

        register_use_case = RegisterUserUseCase(user_repo, token_manager)
        login_use_case = LoginUserUseCase(user_repo)
        forgot_use_case = ForgotPasswordUseCase(user_repo, token_manager)
        reset_use_case = ResetPasswordUseCase(user_repo, token_manager)

        email = "reset_test@example.com"
        old_password = "OldPassword123!"
        new_password = "NewPassword456!"
        username = "reset_user"

        # 1. 註冊並手動驗證（繞過 US1 的驗證步驟以專注於 US2）
        reg_input = RegisterRequestDTO(
            username=username, email=email, password=old_password
        )
        await register_use_case.execute(reg_input)

        # 從 DB 取得 User 並手動標記為已驗證
        user = await user_repo.get_by_email(email)
        user.is_verified = True
        await user_repo.update(user)

        # 2. 請求重設密碼
        await forgot_use_case.execute(email)
        mock_reset_task.assert_called_once()

        # 從 Redis 取得 Token
        keys = await redis_client.keys("auth:reset:*")
        assert len(keys) == 1
        token = keys[0].decode().split(":")[-1]

        # 3. 使用 Token 重設密碼
        reset_result = await reset_use_case.execute(token, new_password)
        assert reset_result is True

        # 4. 嘗試以舊密碼登入 -> 應失敗
        login_input_old = LoginRequestDTO(email=email, password=old_password)
        with pytest.raises(InvalidCredentialsError):
            await login_use_case.execute(login_input_old)

        # 5. 嘗試以新密碼登入 -> 應成功
        login_input_new = LoginRequestDTO(email=email, password=new_password)
        login_output = await login_use_case.execute(login_input_new)
        assert login_output.access_token is not None

        # 6. Token 應已失效
        with pytest.raises(ValueError):
            await reset_use_case.execute(token, "EvenNewer123!")
