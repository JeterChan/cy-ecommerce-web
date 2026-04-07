"""
Integration Tests for User Profile API (US1 - View Profile)

測試範圍：
- GET /api/v1/auth/me/profile 端點
- GetProfileUseCase 完整流程
- UserProfileResponse DTO 欄位驗證
- 未授權 / 使用者不存在的錯誤處理

執行環境：
- 需要 PostgreSQL 服務運行（Docker Compose）
- pythonpath = src（已在 pytest.ini 設定）

執行方式：
    pytest tests/modules/auth/test_user_profile.py -v
"""

import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
import os

from infrastructure.database import Base
from modules.auth.infrastructure.repositories.user_repository import UserRepository
from modules.auth.application.use_cases.get_profile import GetProfileUseCase
from modules.auth.application.dtos import UserProfileResponse
from modules.auth.domain.entities.UserEntity import UserEntity
from core.exceptions import UserNotFoundError
from core.security import get_password_hash

# ==================== Test Database Configuration ====================

TEST_DB_USER = os.getenv("TEST_DB_USER", "user")
TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "password")
TEST_DB_HOST = os.getenv("TEST_DB_HOST", "localhost")
TEST_DB_PORT = os.getenv("TEST_DB_PORT", "5432")
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "test_ecommerce_db")

TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASSWORD}@"
    f"{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
)


# ==================== Fixtures ====================


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """建立測試用的 async 資料庫引擎，每個測試函式前後清空 schema。"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine) -> AsyncSession:
    """提供測試用的 AsyncSession，測試後自動 rollback。"""
    AsyncTestingSessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with AsyncTestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def user_repository(async_session) -> UserRepository:
    """提供 UserRepository 實例。"""
    return UserRepository(async_session)


@pytest_asyncio.fixture
async def get_profile_use_case(user_repository) -> GetProfileUseCase:
    """提供 GetProfileUseCase 實例。"""
    return GetProfileUseCase(user_repository)


@pytest_asyncio.fixture
async def existing_user(user_repository) -> UserEntity:
    """在資料庫中建立一個標準測試使用者並回傳 UserEntity。"""
    user = UserEntity(
        username="profile_tester",
        email="profile_tester@example.com",
        password_hash=get_password_hash("SecurePass123!"),
        is_active=True,
        phone="0912345678",
        address="台北市信義區信義路五段7號",
        carrier_type="MOBILE",
        carrier_number="/ABC1234",
        tax_id=None,
    )
    created = await user_repository.create(user)
    return created


@pytest_asyncio.fixture
async def existing_user_minimal(user_repository) -> UserEntity:
    """建立一個只有必填欄位的測試使用者（選填欄位皆為 None）。"""
    user = UserEntity(
        username="minimal_user",
        email="minimal@example.com",
        password_hash=get_password_hash("SecurePass123!"),
        is_active=True,
    )
    created = await user_repository.create(user)
    return created


# ==================== Tests ====================


@pytest.mark.integration
@pytest.mark.asyncio
class TestGetProfileUseCase:
    """GetProfileUseCase 整合測試"""

    # ---- 成功案例 ----

    async def test_get_profile_returns_correct_dto(
        self,
        get_profile_use_case: GetProfileUseCase,
        existing_user: UserEntity,
    ):
        """成功取得個人檔案，並驗證所有欄位正確對應。"""
        result = await get_profile_use_case.execute(existing_user.id)

        assert isinstance(result, UserProfileResponse)
        assert result.user_id == str(existing_user.id)
        assert result.username == "profile_tester"
        assert result.email == "profile_tester@example.com"
        assert result.phone == "0912345678"
        assert result.address == "台北市信義區信義路五段7號"
        assert result.carrier_type == "MOBILE"
        assert result.carrier_number == "/ABC1234"
        assert result.tax_id is None
        assert result.is_active is True

    async def test_get_profile_timestamps_are_present(
        self,
        get_profile_use_case: GetProfileUseCase,
        existing_user: UserEntity,
    ):
        """驗證 created_at 與 updated_at 欄位存在且為 ISO 格式字串。"""
        result = await get_profile_use_case.execute(existing_user.id)

        assert result.created_at is not None
        assert isinstance(result.created_at, str)
        assert "T" in result.created_at  # ISO 8601 格式

        assert result.updated_at is not None
        assert isinstance(result.updated_at, str)

    async def test_get_profile_optional_fields_none(
        self,
        get_profile_use_case: GetProfileUseCase,
        existing_user_minimal: UserEntity,
    ):
        """取得只有必填欄位的使用者個人檔案，選填欄位應為 None。"""
        result = await get_profile_use_case.execute(existing_user_minimal.id)

        assert result.phone is None
        assert result.address is None
        assert result.carrier_type is None
        assert result.carrier_number is None
        assert result.tax_id is None
        assert result.is_active is True

    async def test_get_profile_user_id_is_string(
        self,
        get_profile_use_case: GetProfileUseCase,
        existing_user: UserEntity,
    ):
        """確認 user_id 在 DTO 中被序列化為字串。"""
        result = await get_profile_use_case.execute(existing_user.id)

        assert isinstance(result.user_id, str)
        # 驗證是合法的 UUID 字串格式
        from uuid import UUID

        parsed = UUID(result.user_id)
        assert parsed == existing_user.id

    # ---- 錯誤案例 ----

    async def test_get_profile_raises_user_not_found(
        self,
        get_profile_use_case: GetProfileUseCase,
    ):
        """查詢不存在的使用者 ID 應拋出 UserNotFoundError。"""
        non_existent_id = uuid4()

        with pytest.raises(UserNotFoundError):
            await get_profile_use_case.execute(non_existent_id)

    async def test_get_profile_wrong_user_id_type_raises(
        self,
        get_profile_use_case: GetProfileUseCase,
    ):
        """查詢另一個不存在的 UUID 確保每次都是獨立的。"""
        another_non_existent_id = uuid4()

        with pytest.raises(UserNotFoundError):
            await get_profile_use_case.execute(another_non_existent_id)


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserProfileResponseDTO:
    """UserProfileResponse DTO 單元測試（不需 DB）"""

    def test_from_entity_maps_all_fields(self):
        """from_entity() 應正確將 UserEntity 的所有欄位對應到 DTO。"""
        from datetime import datetime, timezone

        now = datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        entity = UserEntity(
            username="dto_test_user",
            email="dto@example.com",
            password_hash="hashed",
            is_active=True,
            phone="0987654321",
            address="高雄市前鎮區",
            carrier_type="CITIZEN_CARD",
            carrier_number="AB12345678",
            tax_id="12345678",
            created_at=now,
            updated_at=now,
        )

        dto = UserProfileResponse.from_entity(entity)

        assert dto.username == "dto_test_user"
        assert dto.email == "dto@example.com"
        assert dto.phone == "0987654321"
        assert dto.address == "高雄市前鎮區"
        assert dto.carrier_type == "CITIZEN_CARD"
        assert dto.carrier_number == "AB12345678"
        assert dto.tax_id == "12345678"
        assert dto.is_active is True
        assert "2025" in dto.created_at
        assert "2025" in dto.updated_at

    def test_from_entity_updated_at_fallback_to_created_at(self):
        """當 updated_at 為 None 時，應使用 created_at 的值。"""
        from datetime import datetime, timezone
        from types import SimpleNamespace

        now = datetime(2025, 3, 1, 8, 0, 0, tzinfo=timezone.utc)
        # Use SimpleNamespace to simulate an entity with updated_at=None
        # (bypasses Pydantic validation since UserEntity requires updated_at)
        entity = SimpleNamespace(
            id=None,
            username="fallback_user",
            email="fallback@example.com",
            password_hash="hashed",
            is_active=True,
            created_at=now,
            updated_at=None,
            phone=None,
            address=None,
            carrier_type=None,
            carrier_number=None,
            tax_id=None,
            deleted_at=None,
        )

        dto = UserProfileResponse.from_entity(entity)

        assert dto.updated_at == now.isoformat()

    def test_from_entity_user_id_is_str(self):
        """from_entity() 回傳的 user_id 必須是字串型態。"""
        entity = UserEntity(
            username="str_id_user",
            email="strid@example.com",
            password_hash="hashed",
        )

        dto = UserProfileResponse.from_entity(entity)

        assert isinstance(dto.user_id, str)


# ==================== HTTP Endpoint Tests ====================


@pytest.mark.integration
@pytest.mark.asyncio
class TestGetProfileEndpoint:
    """GET /api/v1/auth/me/profile HTTP 端點整合測試"""

    async def test_get_profile_returns_200_with_valid_token(
        self,
        async_session: AsyncSession,
        existing_user: UserEntity,
    ):
        """使用有效 JWT Token 呼叫端點，應回傳 HTTP 200 及正確個人檔案欄位。"""
        import httpx
        from httpx import ASGITransport
        from main import app
        from infrastructure.database import get_db, get_redis
        from core.security import create_access_token
        from unittest.mock import AsyncMock

        # 產生測試用 access token
        access_token = create_access_token({"sub": existing_user.email})

        # 覆寫 DB / Redis 依賴，使用測試用 session
        async def override_get_db():
            yield async_session

        async def override_get_redis():
            yield AsyncMock()

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_redis] = override_get_redis

        try:
            async with httpx.AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(
                    "/api/v1/auth/me/profile",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["username"] == existing_user.username
            assert data["email"] == str(existing_user.email)
            assert data["phone"] == existing_user.phone
            assert data["address"] == existing_user.address
            assert "user_id" in data
            assert "created_at" in data
        finally:
            app.dependency_overrides.clear()

    async def test_get_profile_returns_401_without_token(
        self,
        async_session: AsyncSession,
    ):
        """未提供 Token 時，端點應回傳 HTTP 403（HTTPBearer auto_error=True 行為）。"""
        import httpx
        from httpx import ASGITransport
        from main import app
        from infrastructure.database import get_db, get_redis
        from unittest.mock import AsyncMock

        async def override_get_db():
            yield async_session

        async def override_get_redis():
            yield AsyncMock()

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_redis] = override_get_redis

        try:
            async with httpx.AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/api/v1/auth/me/profile")

            assert response.status_code == 403
        finally:
            app.dependency_overrides.clear()

    async def test_get_profile_returns_401_with_invalid_token(
        self,
        async_session: AsyncSession,
    ):
        import httpx
        from httpx import ASGITransport
        from main import app
        from infrastructure.database import get_db, get_redis
        from unittest.mock import AsyncMock

        async def override_get_db():
            yield async_session

        async def override_get_redis():
            yield AsyncMock()

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_redis] = override_get_redis

        try:
            async with httpx.AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(
                    "/api/v1/auth/me/profile",
                    headers={"Authorization": "Bearer invalid.token.here"},
                )

            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()


# ==================== UpdateProfile Tests ====================


@pytest.mark.integration
@pytest.mark.asyncio
class TestUpdateProfileUseCase:
    """UpdateProfileUseCase 整合測試"""

    async def test_update_phone_and_address(
        self,
        user_repository: UserRepository,
        existing_user: UserEntity,
    ):
        """更新 phone 和 address，其他欄位不受影響。"""
        from modules.auth.application.use_cases.update_profile import (
            UpdateProfileUseCase,
        )
        from modules.auth.application.dtos.inputs import UpdateProfileRequest

        use_case = UpdateProfileUseCase(user_repository)
        request = UpdateProfileRequest(phone="0987654321", address="新北市板橋區")

        result = await use_case.execute(existing_user.id, request)

        assert result.phone == "0987654321"
        assert result.address == "新北市板橋區"
        # 未提供的欄位應保持原值
        assert result.carrier_type == existing_user.carrier_type
        assert result.carrier_number == existing_user.carrier_number

    async def test_update_carrier_info(
        self,
        user_repository: UserRepository,
        existing_user: UserEntity,
    ):
        """更新載具資訊。"""
        from modules.auth.application.use_cases.update_profile import (
            UpdateProfileUseCase,
        )
        from modules.auth.application.dtos.inputs import UpdateProfileRequest

        use_case = UpdateProfileUseCase(user_repository)
        request = UpdateProfileRequest(
            carrier_type="CITIZEN_CARD",
            carrier_number="AB12345678",
        )

        result = await use_case.execute(existing_user.id, request)

        assert result.carrier_type == "CITIZEN_CARD"
        assert result.carrier_number == "AB12345678"

    async def test_update_with_invalid_tax_id_raises_validation_error(self):
        """tax_id 格式不符（非8碼數字）應拋出 Pydantic ValidationError。"""
        from modules.auth.application.dtos.inputs import UpdateProfileRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            UpdateProfileRequest(tax_id="ABC")

    async def test_update_nonexistent_user_raises_error(
        self,
        user_repository: UserRepository,
    ):
        """更新不存在的使用者應拋出 UserNotFoundError。"""
        from modules.auth.application.use_cases.update_profile import (
            UpdateProfileUseCase,
        )
        from modules.auth.application.dtos.inputs import UpdateProfileRequest

        use_case = UpdateProfileUseCase(user_repository)
        request = UpdateProfileRequest(phone="0912345678")

        with pytest.raises(UserNotFoundError):
            await use_case.execute(uuid4(), request)


# ==================== RequestEmailChange Tests ====================


@pytest.mark.integration
@pytest.mark.asyncio
class TestRequestEmailChangeUseCase:
    """RequestEmailChangeUseCase 整合測試（使用 Mock Redis）"""

    async def test_request_email_change_stores_tokens(
        self,
        user_repository: UserRepository,
        existing_user: UserEntity,
    ):
        """正常流程：密碼正確且新 Email 未被使用，應儲存 tokens。"""
        from unittest.mock import AsyncMock, MagicMock, patch
        from modules.auth.application.use_cases.request_email_change import (
            RequestEmailChangeUseCase,
        )
        from modules.auth.application.dtos.inputs import EmailChangeRequest
        from infrastructure.redis.token_manager import RedisTokenManager

        mock_redis = AsyncMock()
        token_manager = RedisTokenManager(mock_redis)

        use_case = RequestEmailChangeUseCase(user_repository, token_manager)
        request = EmailChangeRequest(
            new_email="new_profile@example.com",
            password="SecurePass123!",
        )

        # Mock Celery task to avoid Redis broker connection during tests
        with patch(
            "infrastructure.tasks.email_tasks.send_email_change_verification.delay"
        ) as mock_delay:
            await use_case.execute(existing_user.id, request)

        # 驗證 Redis setex 被呼叫（代表 tokens 已儲存）
        assert mock_redis.setex.called

    async def test_request_email_change_with_wrong_password_raises(
        self,
        user_repository: UserRepository,
        existing_user: UserEntity,
    ):
        """密碼錯誤時應拋出 InvalidCredentialsError。"""
        from unittest.mock import AsyncMock
        from modules.auth.application.use_cases.request_email_change import (
            RequestEmailChangeUseCase,
        )
        from modules.auth.application.dtos.inputs import EmailChangeRequest
        from infrastructure.redis.token_manager import RedisTokenManager
        from core.exceptions import InvalidCredentialsError

        mock_redis = AsyncMock()
        token_manager = RedisTokenManager(mock_redis)

        use_case = RequestEmailChangeUseCase(user_repository, token_manager)
        request = EmailChangeRequest(
            new_email="another@example.com",
            password="WrongPassword1",
        )

        with pytest.raises(InvalidCredentialsError):
            await use_case.execute(existing_user.id, request)

    async def test_request_email_change_with_duplicate_email_raises(
        self,
        user_repository: UserRepository,
        existing_user: UserEntity,
        existing_user_minimal: UserEntity,
    ):
        """新 Email 已被使用時應拋出 ValidationError。"""
        from unittest.mock import AsyncMock
        from modules.auth.application.use_cases.request_email_change import (
            RequestEmailChangeUseCase,
        )
        from modules.auth.application.dtos.inputs import EmailChangeRequest
        from infrastructure.redis.token_manager import RedisTokenManager
        from core.exceptions import ValidationError

        mock_redis = AsyncMock()
        token_manager = RedisTokenManager(mock_redis)

        use_case = RequestEmailChangeUseCase(user_repository, token_manager)
        # 使用另一個已存在使用者的 email
        request = EmailChangeRequest(
            new_email=str(existing_user_minimal.email),
            password="SecurePass123!",
        )

        with pytest.raises(ValidationError):
            await use_case.execute(existing_user.id, request)


# ==================== VerifyEmailChange Tests ====================


@pytest.mark.integration
@pytest.mark.asyncio
class TestVerifyEmailChangeUseCase:
    """VerifyEmailChangeUseCase 整合測試（使用 Mock Redis）"""

    async def test_verify_old_email_returns_pending_when_new_not_verified(
        self,
        user_repository: UserRepository,
        existing_user: UserEntity,
    ):
        """驗證舊 Email 後，若新 Email 尚未驗證，應回傳 pending 狀態。"""
        from unittest.mock import AsyncMock
        from modules.auth.application.use_cases.verify_email_change import (
            VerifyEmailChangeUseCase,
        )
        from modules.auth.application.dtos.inputs import (
            VerifyEmailChangeRequest,
            EmailVerifyType,
        )
        from infrastructure.redis.token_manager import RedisTokenManager

        old_token = "valid_old_token_abc"
        mock_redis = AsyncMock()

        # mock: old token 存在且正確（Redis decode_responses=True 回傳 str）
        mock_redis.get = AsyncMock(
            side_effect=lambda key: (
                old_token
                if "old_token" in key
                else "false" if "old_verified" in key or "new_verified" in key else None
            )
        )
        mock_redis.ttl = AsyncMock(return_value=86000)

        token_manager = RedisTokenManager(mock_redis)
        use_case = VerifyEmailChangeUseCase(user_repository, token_manager)

        request = VerifyEmailChangeRequest(token=old_token, type=EmailVerifyType.OLD)
        result = await use_case.execute(str(existing_user.id), request)

        assert result["status"] == "pending"

    async def test_verify_with_invalid_token_raises_validation_error(
        self,
        user_repository: UserRepository,
        existing_user: UserEntity,
    ):
        """無效 Token 應拋出 ValidationError。"""
        from unittest.mock import AsyncMock
        from modules.auth.application.use_cases.verify_email_change import (
            VerifyEmailChangeUseCase,
        )
        from modules.auth.application.dtos.inputs import (
            VerifyEmailChangeRequest,
            EmailVerifyType,
        )
        from infrastructure.redis.token_manager import RedisTokenManager
        from core.exceptions import ValidationError

        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)  # Token 不存在

        token_manager = RedisTokenManager(mock_redis)
        use_case = VerifyEmailChangeUseCase(user_repository, token_manager)

        request = VerifyEmailChangeRequest(
            token="invalid_token", type=EmailVerifyType.NEW
        )

        with pytest.raises(ValidationError):
            await use_case.execute(str(existing_user.id), request)


# ==================== DeleteAccount Tests ====================


@pytest.mark.integration
@pytest.mark.asyncio
class TestDeleteAccountUseCase:
    """DeleteAccountUseCase 整合測試"""

    async def test_soft_delete_sets_is_active_false(
        self,
        user_repository: UserRepository,
        existing_user: UserEntity,
    ):
        """軟刪除後，is_active 應為 False 且 deleted_at 應被設定。"""
        from modules.auth.application.use_cases.delete_account import (
            DeleteAccountUseCase,
        )

        use_case = DeleteAccountUseCase(user_repository)
        await use_case.execute(existing_user.id)

        # 重新查詢確認
        updated_user = await user_repository.get_by_id(existing_user.id)
        assert updated_user is not None
        assert updated_user.is_active is False
        assert updated_user.deleted_at is not None

    async def test_soft_delete_user_cannot_login(
        self,
        user_repository: UserRepository,
        existing_user: UserEntity,
        async_session: AsyncSession,
    ):
        """軟刪除後，使用者應無法登入（is_active=False）。"""
        from modules.auth.application.use_cases.delete_account import (
            DeleteAccountUseCase,
        )

        use_case = DeleteAccountUseCase(user_repository)
        await use_case.execute(existing_user.id)

        deleted_user = await user_repository.get_by_id(existing_user.id)
        assert deleted_user is not None
        assert deleted_user.is_active is False

    async def test_delete_nonexistent_user_raises_error(
        self,
        user_repository: UserRepository,
    ):
        """刪除不存在的使用者應拋出 UserNotFoundError。"""
        from modules.auth.application.use_cases.delete_account import (
            DeleteAccountUseCase,
        )

        use_case = DeleteAccountUseCase(user_repository)

        with pytest.raises(UserNotFoundError):
            await use_case.execute(uuid4())

    async def test_deleted_at_is_recent(
        self,
        user_repository: UserRepository,
        existing_user: UserEntity,
    ):
        """軟刪除後，deleted_at 應為近期時間戳（1 分鐘內）。"""
        from modules.auth.application.use_cases.delete_account import (
            DeleteAccountUseCase,
        )
        from datetime import datetime, timezone, timedelta

        use_case = DeleteAccountUseCase(user_repository)
        await use_case.execute(existing_user.id)

        updated_user = await user_repository.get_by_id(existing_user.id)
        assert updated_user is not None
        assert updated_user.deleted_at is not None

        now = datetime.now(timezone.utc)
        diff = abs((now - updated_user.deleted_at).total_seconds())
        assert diff < 60, f"deleted_at 時間差異過大：{diff} 秒"
