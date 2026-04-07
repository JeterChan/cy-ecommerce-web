"""
個人檔案更新與密碼變更的整合測試
測試範圍：更新使用者名稱 -> 檢查唯一性 -> 變更密碼 -> 以新密碼登入
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import os
from uuid import uuid4

from src.infrastructure.database import Base
from src.modules.auth.domain.entities.UserEntity import UserEntity
from src.modules.auth.infrastructure.repositories.user_repository import UserRepository
from src.modules.auth.application.use_cases.update_profile import UpdateProfileUseCase
from src.modules.auth.application.use_cases.change_password import ChangePasswordUseCase
from src.modules.auth.use_cases.login import LoginUserUseCase
from src.modules.auth.application.dtos import UpdateProfileRequest, LoginRequestDTO
from src.core.exceptions import InvalidCredentialsError, ValidationError

# Test Database Configuration
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/test_ecommerce_db",
)


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
async def test_profile_update_and_password_change_flow(async_session):
    # Arrange
    user_repo = UserRepository(async_session)
    update_use_case = UpdateProfileUseCase(user_repo)
    change_pass_use_case = ChangePasswordUseCase(user_repo)
    login_use_case = LoginUserUseCase(user_repo)

    email = "profile_test@example.com"
    password = "OldPassword123!"
    username = "original_user"

    # 建立初始使用者
    from src.core.security import get_password_hash

    user = UserEntity(
        id=uuid4(),
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        is_verified=True,
        is_active=True,
    )
    await user_repo.create(user)

    # 1. 更新使用者名稱
    new_username = "updated_user"
    update_req = UpdateProfileRequest(username=new_username)
    await update_use_case.execute(user.id, update_req)

    updated_user = await user_repo.get_by_id(user.id)
    assert updated_user.username == new_username

    # 2. 測試使用者名稱唯一性
    other_user = UserEntity(
        id=uuid4(),
        username="taken_name",
        email="other@example.com",
        password_hash="...",
        is_verified=True,
        is_active=True,
    )
    await user_repo.create(other_user)

    with pytest.raises(ValidationError) as exc:
        await update_use_case.execute(
            user.id, UpdateProfileRequest(username="taken_name")
        )
    assert "使用者名稱已存在" in str(exc.value)

    # 3. 變更密碼
    new_password = "NewPassword456!"
    await change_pass_use_case.execute(user.id, password, new_password)

    # 4. 以新密碼登入 -> 應成功
    login_output = await login_use_case.execute(
        LoginRequestDTO(email=email, password=new_password)
    )
    assert login_output.access_token is not None

    # 5. 以舊密碼登入 -> 應失敗
    with pytest.raises(InvalidCredentialsError):
        await login_use_case.execute(LoginRequestDTO(email=email, password=password))
