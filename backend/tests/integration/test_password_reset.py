"""
密碼重設流程的整合測試
測試範圍：請求重設 -> 生成 Token -> 使用 Token 重設密碼 -> 以新密碼登入
"""

import os
from unittest.mock import patch

import pytest
import pytest_asyncio
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.exceptions import InvalidCredentialsError
from infrastructure.database import Base
from infrastructure.redis.token_manager import RedisTokenManager
from modules.auth.application.dtos import LoginRequestDTO, RegisterRequestDTO
from modules.auth.application.use_cases.forgot_password import ForgotPasswordUseCase
from modules.auth.application.use_cases.login import LoginUserUseCase
from modules.auth.application.use_cases.register import RegisterUserUseCase
from modules.auth.application.use_cases.reset_password import ResetPasswordUseCase
from modules.auth.infrastructure.password_hasher import BcryptPasswordHasher
from modules.auth.infrastructure.repository import UserRepository

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
async def test_password_reset_flow_integration(async_session, redis_client):
    # Arrange
    user_repo = UserRepository(async_session)
    password_hasher = BcryptPasswordHasher()
    token_manager = RedisTokenManager(redis_client)

    with (
        patch(
            "modules.auth.application.use_cases.register.send_registration_verification"
        ),
        patch(
            "modules.auth.application.use_cases.forgot_password.send_password_reset.delay"
        ) as mock_reset_task,
    ):
        register_use_case = RegisterUserUseCase(user_repo, token_manager)
        login_use_case = LoginUserUseCase(user_repo, password_hasher)
        forgot_use_case = ForgotPasswordUseCase(user_repo, token_manager)
        reset_use_case = ResetPasswordUseCase(user_repo, token_manager)

        email = "reset_test@example.com"
        old_password = "OldPassword123!"
        new_password = "NewPassword456!"
        username = "reset_user"

        # 1. 註冊
        reg_input = RegisterRequestDTO(
            username=username, email=email, password=old_password
        )
        await register_use_case.execute(reg_input)

        # 手動標記為已驗證
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

        # 4. 以舊密碼登入 -> 應失敗
        login_input_old = LoginRequestDTO(email=email, password=old_password)
        with pytest.raises(InvalidCredentialsError):
            await login_use_case.execute(login_input_old)

        # 5. 以新密碼登入 -> 應成功
        login_input_new = LoginRequestDTO(email=email, password=new_password)
        login_output = await login_use_case.execute(login_input_new)
        assert login_output.access_token is not None

        # 6. Token 應已失效
        with pytest.raises(ValueError):
            await reset_use_case.execute(token, "EvenNewer123!")
