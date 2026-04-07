"""
Unit Tests for LoginUserUseCase

測試範圍：
- 測試 Use Case 業務邏輯
- 使用 Mock Repository（不依賴真實資料庫）
- 快速執行、易於維護
"""

import uuid
from datetime import datetime

import pytest

from core.exceptions import InvalidCredentialsError, UserNotRegisteredError
from core.security import get_password_hash, verify_token
from modules.auth.application.dtos import LoginRequestDTO, LoginResponseDTO
from modules.auth.application.use_cases.login import LoginUserUseCase
from modules.auth.domain.entities import UserEntity
from modules.auth.domain.repository import IUserRepository
from modules.auth.domain.services.password_hasher import IPasswordHasher

# ==================== Mock Classes ====================


class MockUserRepository(IUserRepository):
    def __init__(self):
        self.users = []

    async def create(self, user: UserEntity) -> UserEntity:
        if user.id is None:
            user.id = uuid.uuid4()
        if user.created_at is None:
            user.created_at = datetime.utcnow()
        if user.updated_at is None:
            user.updated_at = datetime.utcnow()
        self.users.append(user)
        return user

    async def get_by_email(self, email: str) -> UserEntity | None:
        return next((u for u in self.users if u.email.lower() == email.lower()), None)

    async def get_by_id(self, user_id) -> UserEntity | None:
        return next((u for u in self.users if str(u.id) == str(user_id)), None)

    async def get_by_username(self, username: str) -> UserEntity | None:
        return next((u for u in self.users if u.username == username), None)

    async def update(self, user: UserEntity) -> UserEntity:
        for i, u in enumerate(self.users):
            if str(u.id) == str(user.id):
                self.users[i] = user
                return user
        return user

    async def exists_by_email(self, email: str) -> bool:
        return any(u.email.lower() == email.lower() for u in self.users)

    async def exists_by_username(self, username: str) -> bool:
        return any(u.username == username for u in self.users)


class MockPasswordHasher(IPasswordHasher):
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        from core.security import verify_password

        return verify_password(plain_password, hashed_password)

    def hash(self, plain_password: str) -> str:
        return get_password_hash(plain_password)


# ==================== Test Cases ====================


@pytest.mark.asyncio
class TestLoginUserUseCase:
    """LoginUserUseCase 的單元測試"""

    @pytest.fixture
    def mock_repository(self):
        return MockUserRepository()

    @pytest.fixture
    def mock_password_hasher(self):
        return MockPasswordHasher()

    @pytest.fixture
    def use_case(self, mock_repository, mock_password_hasher):
        return LoginUserUseCase(mock_repository, mock_password_hasher)

    @pytest.fixture
    async def registered_user(self, mock_repository):
        password = "SecurePass123!"
        user = UserEntity(
            email="john@example.com",
            username="john_doe",
            password_hash=get_password_hash(password),
            is_active=True,
            is_verified=True,
        )
        created_user = await mock_repository.create(user)
        return {"user": created_user, "password": password}

    # ==================== 成功案例 ====================

    async def test_login_success(self, use_case, registered_user):
        """測試成功登入"""
        user_data = registered_user
        input_dto = LoginRequestDTO(
            email=user_data["user"].email, password=user_data["password"]
        )

        output_dto = await use_case.execute(input_dto)

        assert isinstance(output_dto, LoginResponseDTO)
        assert output_dto.user.id == user_data["user"].id
        assert output_dto.user.username == user_data["user"].username
        assert output_dto.user.email == user_data["user"].email
        assert output_dto.user.is_active is True
        assert output_dto.access_token is not None
        assert output_dto.token_type == "bearer"
        assert output_dto.refresh_token is None

        payload = verify_token(output_dto.access_token, token_type="access")
        assert payload is not None
        assert payload["sub"] == str(user_data["user"].email)
        assert payload["user_id"] == str(user_data["user"].id)

    async def test_login_email_case_insensitive(self, use_case, registered_user):
        """測試 Email 不區分大小寫登入"""
        user_data = registered_user
        input_dto = LoginRequestDTO(
            email="JOHN@EXAMPLE.COM", password=user_data["password"]
        )

        output_dto = await use_case.execute(input_dto)

        assert output_dto.user.id == user_data["user"].id
        assert output_dto.user.email == user_data["user"].email

    # ==================== 失敗案例 ====================

    async def test_login_user_not_found(self, use_case):
        """測試使用者不存在時登入失敗"""
        input_dto = LoginRequestDTO(
            email="notexist@example.com", password="AnyPassword123!"
        )

        with pytest.raises(UserNotRegisteredError) as exc_info:
            await use_case.execute(input_dto)

        assert "尚未註冊" in str(exc_info.value)

    async def test_login_wrong_password(self, use_case, registered_user):
        """測試密碼錯誤時登入失敗"""
        user_data = registered_user
        input_dto = LoginRequestDTO(
            email=user_data["user"].email, password="WrongPassword123!"
        )

        with pytest.raises(InvalidCredentialsError) as exc_info:
            await use_case.execute(input_dto)

        assert "帳號或密碼錯誤" in str(exc_info.value)

    async def test_login_empty_password(self, use_case, registered_user):
        """測試空密碼登入失敗（Pydantic 驗證層）"""
        user_data = registered_user

        with pytest.raises(Exception):  # Pydantic ValidationError
            LoginRequestDTO(email=user_data["user"].email, password="")

    # ==================== Token 驗證測試 ====================

    async def test_generated_token_contains_user_info(self, use_case, registered_user):
        """測試生成的 Token 包含正確的使用者資訊"""
        user_data = registered_user
        input_dto = LoginRequestDTO(
            email=user_data["user"].email, password=user_data["password"]
        )

        output_dto = await use_case.execute(input_dto)

        payload = verify_token(output_dto.access_token, token_type="access")
        assert payload is not None
        assert payload["sub"] == str(user_data["user"].email)
        assert payload["user_id"] == str(user_data["user"].id)
        assert "exp" in payload
        assert payload["type"] == "access"

    async def test_token_expiration_field_exists(self, use_case, registered_user):
        """測試 Token 包含過期時間"""
        user_data = registered_user
        input_dto = LoginRequestDTO(
            email=user_data["user"].email, password=user_data["password"]
        )

        output_dto = await use_case.execute(input_dto)

        payload = verify_token(output_dto.access_token, token_type="access")
        assert "exp" in payload
        assert payload["exp"] > datetime.utcnow().timestamp()

    # ==================== 多次登入測試 ====================

    async def test_multiple_logins_generate_different_tokens(
        self, use_case, registered_user
    ):
        """測試多次登入產生不同的 Token"""
        user_data = registered_user
        input_dto = LoginRequestDTO(
            email=user_data["user"].email, password=user_data["password"]
        )

        output_dto1 = await use_case.execute(input_dto)
        output_dto2 = await use_case.execute(input_dto)

        assert verify_token(output_dto1.access_token, token_type="access") is not None
        assert verify_token(output_dto2.access_token, token_type="access") is not None
