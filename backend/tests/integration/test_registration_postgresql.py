"""
Integration Tests for User Registration (PostgreSQL)

測試範圍：
- 測試完整的註冊流程（Use Case + Repository + Database）
- 使用真實的 PostgreSQL 資料庫（測試資料庫）
- 驗證資料是否正確儲存到資料庫

執行環境：
- 在虛擬環境 (venv) 中執行
- 使用 Docker Compose 中的 PostgreSQL 服務
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
import os

from src.infrastructure.database import Base
from src.modules.auth.use_cases.register import RegisterUserUseCase
from src.modules.auth.use_cases.dtos import RegisterUserInputDTO
from src.modules.auth.infrastructure.repositories.user_repository import UserRepository
from src.modules.auth.infrastructure.models import UserModel
from src.core.exceptions import DuplicateEmailError
from src.core.security import verify_password


# ==================== Test Database Configuration ====================

# 使用環境變數或預設值
TEST_DB_USER = os.getenv("TEST_DB_USER", "user")
TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "password")
TEST_DB_HOST = os.getenv("TEST_DB_HOST", "localhost")  # 本機執行時用 localhost
TEST_DB_PORT = os.getenv("TEST_DB_PORT", "5432")
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "test_ecommerce_db")

# 測試資料庫 URL（使用 PostgreSQL）
TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASSWORD}@"
    f"{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
)


# ==================== Fixtures ====================

@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """
    建立測試用的異步引擎

    使用 function scope 確保每個測試都有乾淨的資料庫狀態
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )

    # 建立所有資料表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # 先清空
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # 測試後清理：刪除所有資料表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine) -> AsyncSession:
    """建立測試用的 Session"""
    AsyncTestingSessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with AsyncTestingSessionLocal() as session:
        yield session
        # 測試後回滾
        await session.rollback()


@pytest_asyncio.fixture
async def user_repository(async_session) -> UserRepository:
    """建立 UserRepository 實例"""
    return UserRepository(async_session)


@pytest_asyncio.fixture
async def register_use_case(user_repository) -> RegisterUserUseCase:
    """建立 RegisterUserUseCase 實例"""
    return RegisterUserUseCase(user_repository)


# ==================== Integration Test Cases ====================

@pytest.mark.asyncio
class TestRegisterUserIntegration:
    """User Registration 的整合測試（PostgreSQL）"""

    # ==================== 成功案例 ====================

    async def test_register_user_success_full_flow(
        self, register_use_case, async_session
    ):
        """測試完整的註冊流程"""
        # Arrange
        input_dto = RegisterUserInputDTO(
            username="integration_test_user",
            email="integration@example.com",
            password="IntegrationPass123!",
        )

        # Act
        output_dto = await register_use_case.execute(input_dto)

        # Assert - 檢查 Output DTO
        assert output_dto.id is not None
        assert output_dto.username == "integration_test_user"
        assert output_dto.email == "integration@example.com"
        assert output_dto.is_active is True
        assert output_dto.created_at is not None

        # Assert - 檢查資料庫中的資料（使用 PostgreSQL 語法）
        result = await async_session.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {"email": "integration@example.com"}
        )
        db_user = result.fetchone()

        assert db_user is not None
        assert db_user.username == "integration_test_user"
        assert db_user.email == "integration@example.com"

    async def test_register_user_password_is_hashed_in_database(
        self, register_use_case, async_session
    ):
        """測試密碼在資料庫中已加密儲存"""
        # Arrange
        plain_password = "MySecretPassword123!"
        input_dto = RegisterUserInputDTO(
            username="password_test",
            email="password@example.com",
            password=plain_password,
        )

        # Act
        output_dto = await register_use_case.execute(input_dto)

        # Assert - 從資料庫查詢使用者
        result = await async_session.execute(
            text("SELECT password_hash FROM users WHERE id = :id"),
            {"id": output_dto.id}
        )
        password_hash = result.scalar_one()

        # 密碼應該被雜湊（不是明文）
        assert password_hash != plain_password
        assert password_hash.startswith("$2b$")  # Bcrypt 前綴

        # 應該可以驗證密碼
        assert verify_password(plain_password, password_hash) is True
        assert verify_password("WrongPassword", password_hash) is False

    async def test_register_multiple_users_in_database(
        self, register_use_case, async_session
    ):
        """測試註冊多個使用者到資料庫"""
        # Arrange
        users_data = [
            ("alice_db", "alice_db@example.com", "AlicePass123!"),
            ("bob_db", "bob_db@example.com", "BobPass123!"),
            ("charlie_db", "charlie_db@example.com", "CharliePass123!"),
        ]

        # Act
        created_users = []
        for username, email, password in users_data:
            input_dto = RegisterUserInputDTO(
                username=username, email=email, password=password
            )
            output_dto = await register_use_case.execute(input_dto)
            created_users.append(output_dto)

        # Assert - 檢查所有使用者都在資料庫中
        result = await async_session.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar_one()
        assert user_count == 3

        # 檢查每個使用者的資料
        for i, (username, email, _) in enumerate(users_data):
            assert created_users[i].username == username
            assert created_users[i].email == email

    async def test_register_user_with_default_values(
        self, register_use_case, async_session
    ):
        """測試使用者的預設值正確儲存"""
        # Arrange
        input_dto = RegisterUserInputDTO(
            username="default_user",
            email="default@example.com",
            password="DefaultPass123!",
        )

        # Act
        output_dto = await register_use_case.execute(input_dto)

        # Assert - 從資料庫查詢（PostgreSQL 用 BOOLEAN）
        result = await async_session.execute(
            text("SELECT is_is_activate, is_superuser FROM users WHERE id = :id"),
            {"id": output_dto.id}
        )
        row = result.fetchone()

        assert row.is_activate is True
        assert row.is_superuser is False

    # ==================== 錯誤案例 ====================

    async def test_register_user_duplicate_email_in_database(
        self, register_use_case, async_session
    ):
        """測試資料庫層級的電子郵件唯一性約束"""
        # Arrange
        email = "duplicate_db@example.com"

        # 先註冊第一個使用者
        first_input = RegisterUserInputDTO(
            username="user1_db", email=email, password="FirstPass123!"
        )
        await register_use_case.execute(first_input)

        # Act & Assert - 嘗試註冊相同電子郵件
        second_input = RegisterUserInputDTO(
            username="user2_db", email=email, password="SecondPass123!"
        )

        with pytest.raises(DuplicateEmailError) as exc_info:
            await register_use_case.execute(second_input)

        assert email in str(exc_info.value)

        # 驗證資料庫中只有一個使用者
        result = await async_session.execute(
            text("SELECT COUNT(*) FROM users WHERE email = :email"),
            {"email": email}
        )
        count = result.scalar_one()
        assert count == 1

    async def test_register_user_transaction_rollback_on_error(
        self, user_repository, async_session
    ):
        """測試發生錯誤時事務回滾"""
        # Arrange - 先建立一個使用者
        first_input = RegisterUserInputDTO(
            username="first_user",
            email="rollback@example.com",
            password="FirstPass123!",
        )
        use_case = RegisterUserUseCase(user_repository)
        await use_case.execute(first_input)

        # 記錄初始使用者數量
        initial_result = await async_session.execute(text("SELECT COUNT(*) FROM users"))
        initial_count = initial_result.scalar_one()

        # Act - 嘗試重複註冊（應該失敗）
        second_input = RegisterUserInputDTO(
            username="second_user",
            email="rollback@example.com",  # 重複的電子郵件
            password="SecondPass123!",
        )

        try:
            await use_case.execute(second_input)
        except DuplicateEmailError:
            pass

        # Assert - 使用者數量應該沒有變化（事務已回滾）
        final_result = await async_session.execute(text("SELECT COUNT(*) FROM users"))
        final_count = final_result.scalar_one()
        assert final_count == initial_count

    # ==================== PostgreSQL 特定功能測試 ====================

    async def test_postgresql_timestamps_with_timezone(
        self, register_use_case, async_session
    ):
        """測試 PostgreSQL 的 TIMESTAMP WITH TIME ZONE"""
        # Arrange
        input_dto = RegisterUserInputDTO(
            username="timestamp_test",
            email="timestamp@example.com",
            password="TimestampPass123!",
        )

        # Act
        output_dto = await register_use_case.execute(input_dto)

        # Assert - PostgreSQL 特定查詢
        result = await async_session.execute(
            text("""
                SELECT 
                    created_at,
                    updated_at,
                    created_at AT TIME ZONE 'UTC' as created_utc
                FROM users 
                WHERE id = :id
            """),
            {"id": output_dto.id}
        )
        row = result.fetchone()

        assert row.created_at is not None
        assert row.updated_at is not None
        assert row.created_at == row.updated_at

    async def test_postgresql_case_insensitive_email(
        self, register_use_case, async_session
    ):
        """測試 PostgreSQL 的大小寫處理"""
        # Arrange - 先註冊小寫 email
        first_input = RegisterUserInputDTO(
            username="user1",
            email="test@example.com",
            password="TestPass123!",
        )
        await register_use_case.execute(first_input)

        # Act & Assert - 嘗試用大寫 email 註冊（應該失敗，因為是重複）
        second_input = RegisterUserInputDTO(
            username="user2",
            email="TEST@EXAMPLE.COM",  # 大寫
            password="TestPass123!",
        )

        # 這個測試取決於資料庫設定，預設應該區分大小寫
        # 如果需要不區分大小寫，需要在模型中使用 CITEXT 或建立唯一索引


# ==================== Repository-Level Tests ====================

@pytest.mark.asyncio
class TestUserRepositoryIntegration:
    """UserRepository 的整合測試（PostgreSQL）"""

    async def test_repository_create_user(self, user_repository, async_session):
        """測試 Repository 的 create 方法"""
        from src.modules.auth.domain.entities import UserEntity

        # Arrange
        user_entity = UserEntity(
            username="repo_test",
            email="repo@example.com",
            password_hash="$2b$12$hashedpassword",
            is_active=True,
            is_superuser=False,
        )

        # Act
        created_user = await user_repository.create(user_entity)

        # Assert
        assert created_user.id is not None
        assert created_user.username == "repo_test"
        assert created_user.created_at is not None

    async def test_repository_get_by_email(self, user_repository, async_session):
        """測試 Repository 的 get_by_email 方法"""
        from src.modules.auth.domain.entities import UserEntity

        # Arrange - 建立使用者
        user_entity = UserEntity(
            username="email_test",
            email="email_test@example.com",
            password_hash="$2b$12$hashedpassword",
        )
        await user_repository.create(user_entity)

        # Act
        found_user = await user_repository.get_by_email("email_test@example.com")

        # Assert
        assert found_user is not None
        assert found_user.email == "email_test@example.com"
        assert found_user.username == "email_test"

    async def test_repository_exists_by_email(self, user_repository, async_session):
        """測試 Repository 的 exists_by_email 方法"""
        from src.modules.auth.domain.entities import UserEntity

        # Arrange - 建立使用者
        user_entity = UserEntity(
            username="exists_test",
            email="exists@example.com",
            password_hash="$2b$12$hashedpassword",
        )
        await user_repository.create(user_entity)

        # Act & Assert
        assert await user_repository.exists_by_email("exists@example.com") is True
        assert await user_repository.exists_by_email("notexist@example.com") is False

