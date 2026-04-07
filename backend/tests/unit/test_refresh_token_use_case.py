"""
Unit Tests for RefreshTokenUseCase

測試範圍：
- 測試 Refresh Token Use Case 業務邏輯
- 使用 Mock Repository（不依賴真實資料庫）
- 快速執行、易於維護
"""

import uuid
from datetime import datetime

import pytest

from core.exceptions import InvalidCredentialsError
from core.security import create_refresh_token, get_password_hash, verify_token
from modules.auth.application.dtos import RefreshTokenRequestDTO, TokenResponseDTO
from modules.auth.application.use_cases.refresh_token import RefreshTokenUseCase
from modules.auth.domain.entities import UserEntity
from modules.auth.domain.repository import IUserRepository


# ==================== Mock Repository ====================


class MockUserRepository(IUserRepository):
    """Mock User Repository for Unit Testing"""

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


# ==================== Test Cases ====================


@pytest.mark.asyncio
class TestRefreshTokenUseCase:
    """RefreshTokenUseCase 的單元測試"""

    @pytest.fixture
    def mock_repository(self):
        return MockUserRepository()

    @pytest.fixture
    def use_case(self, mock_repository):
        return RefreshTokenUseCase(mock_repository)

    @pytest.fixture
    async def active_user(self, mock_repository):
        user = UserEntity(
            email="john@example.com",
            username="john_doe",
            password_hash=get_password_hash("SecurePass123!"),
            is_active=True,
        )
        return await mock_repository.create(user)

    @pytest.fixture
    async def inactive_user(self, mock_repository):
        user = UserEntity(
            email="inactive@example.com",
            username="inactive_user",
            password_hash=get_password_hash("SecurePass123!"),
            is_active=False,
        )
        return await mock_repository.create(user)

    # ==================== 成功案例 ====================

    async def test_refresh_token_success(self, use_case, active_user):
        """測試成功刷新 Token"""
        token_data = {
            "sub": str(active_user.email),
            "user_id": str(active_user.id),
        }
        refresh_token = create_refresh_token(data=token_data)
        input_dto = RefreshTokenRequestDTO(refresh_token=refresh_token)

        output_dto = await use_case.execute(input_dto)

        assert isinstance(output_dto, TokenResponseDTO)
        assert output_dto.access_token is not None
        assert output_dto.token_type == "bearer"

        payload = verify_token(output_dto.access_token, token_type="access")
        assert payload is not None
        assert payload["sub"] == str(active_user.email)
        assert payload["user_id"] == str(active_user.id)

    # ==================== 失敗案例 ====================

    async def test_refresh_token_invalid_token(self, use_case):
        """測試無效的 Refresh Token"""
        input_dto = RefreshTokenRequestDTO(refresh_token="invalid.token.here")

        with pytest.raises(InvalidCredentialsError) as exc_info:
            await use_case.execute(input_dto)

        assert "帳號或密碼錯誤" in str(exc_info.value)

    async def test_refresh_token_user_not_found(self, use_case):
        """測試使用者不存在時刷新失敗"""
        token_data = {
            "sub": "nonexistent@example.com",
            "user_id": str(uuid.uuid4()),
        }
        refresh_token = create_refresh_token(data=token_data)
        input_dto = RefreshTokenRequestDTO(refresh_token=refresh_token)

        with pytest.raises(InvalidCredentialsError) as exc_info:
            await use_case.execute(input_dto)

        assert "帳號或密碼錯誤" in str(exc_info.value)

    async def test_refresh_token_inactive_user(self, use_case, inactive_user):
        """測試未啟用使用者無法刷新 Token"""
        token_data = {
            "sub": str(inactive_user.email),
            "user_id": str(inactive_user.id),
        }
        refresh_token = create_refresh_token(data=token_data)
        input_dto = RefreshTokenRequestDTO(refresh_token=refresh_token)

        with pytest.raises(InvalidCredentialsError) as exc_info:
            await use_case.execute(input_dto)

        assert "帳號或密碼錯誤" in str(exc_info.value)

    async def test_refresh_token_with_access_token(self, use_case, active_user):
        """測試使用 Access Token 來刷新（應該失敗）"""
        from core.security import create_access_token

        token_data = {
            "sub": str(active_user.email),
            "user_id": str(active_user.id),
        }
        access_token = create_access_token(data=token_data)
        input_dto = RefreshTokenRequestDTO(refresh_token=access_token)

        with pytest.raises(InvalidCredentialsError) as exc_info:
            await use_case.execute(input_dto)

        assert "帳號或密碼錯誤" in str(exc_info.value)
