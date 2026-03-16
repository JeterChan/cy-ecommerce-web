"""
帳號刪除流程的整合測試
測試範圍：驗證密碼 -> 軟刪除 -> 無法登入 -> Email 資源釋出 (可重新註冊)
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import os
from uuid import uuid4

from src.infrastructure.database import Base
from src.modules.auth.domain.entities.UserEntity import UserEntity
from src.modules.auth.infrastructure.repositories.user_repository import UserRepository
from src.modules.auth.application.use_cases.delete_account import DeleteAccountUseCase
from src.modules.auth.use_cases.login import LoginUserUseCase
from src.modules.auth.use_cases.register import RegisterUserUseCase
from src.modules.auth.application.dtos.inputs import LoginRequestDTO, RegisterRequestDTO
from src.core.exceptions import InvalidCredentialsError, UserNotRegisteredError
from src.infrastructure.redis.token_manager import RedisTokenManager
from unittest.mock import patch

# Test Database Configuration
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/test_ecommerce_db")
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

@pytest.mark.asyncio
async def test_account_deletion_flow(async_session):
    # Arrange
    user_repo = UserRepository(async_session)
    delete_use_case = DeleteAccountUseCase(user_repo)
    login_use_case = LoginUserUseCase(user_repo)
    
    # 建立一個 Redis 模擬 (雖然這裡用不到 Redis，但 RegisterUserUseCase 需要)
    from redis.asyncio import Redis
    redis_client = Redis.from_url(TEST_REDIS_URL)
    token_manager = RedisTokenManager(redis_client)
    
    email = "delete_test@example.com"
    password = "SecretPassword123!"
    username = "delete_me"
    
    # 建立初始使用者
    from src.core.security import get_password_hash
    user = UserEntity(
        id=uuid4(),
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        is_verified=True,
        is_active=True
    )
    await user_repo.create(user)
    
    # 1. 嘗試以錯誤密碼刪除 -> 應失敗
    with pytest.raises(InvalidCredentialsError):
        await delete_use_case.execute(user.id, "WrongPassword")
        
    # 2. 嘗試以正確密碼刪除 -> 應成功
    await delete_use_case.execute(user.id, password)
    
    # 3. 嘗試登入已刪除帳號 -> 應失敗 (因為 UserRepository.get_by_email 排除已刪除者)
    with pytest.raises(UserNotRegisteredError):
        await login_use_case.execute(LoginRequestDTO(email=email, password=password))
        
    # 4. 驗證 Email 資源已釋出，可以重新註冊
    with patch("src.modules.auth.use_cases.register.send_registration_verification.delay"):
        register_use_case = RegisterUserUseCase(user_repo, token_manager)
        new_reg_input = RegisterRequestDTO(username="new_user", email=email, password="NewPassword123!")
        new_reg_output = await register_use_case.execute(new_reg_input)
        assert new_reg_output.email == email
    
    await redis_client.close()
