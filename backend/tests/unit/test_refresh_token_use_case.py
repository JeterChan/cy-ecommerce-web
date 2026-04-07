"""
Unit Tests for RefreshTokenUseCase

測試範圍：
- 測試 Refresh Token Use Case 業務邏輯
- 使用 Mock Repository（不依賴真實資料庫）
- 快速執行、易於維護
"""

import pytest
from datetime import datetime
import uuid

from modules.auth.use_cases.refresh import RefreshTokenUseCase
from modules.auth.use_cases.dtos import (
    RefreshTokenInputDTO,
    RefreshTokenOutputDTO,
)
from modules.auth.domain.entities.UserEntity import UserEntity
from modules.auth.domain.repositories.i_user_repository import IUserRepository
from core.exceptions import InvalidCredentialsError
from core.security import get_password_hash, verify_token, create_refresh_token

# ==================== Mock Repository ====================


class MockUserRepository(IUserRepository):
    """Mock User Repository for Unit Testing"""

    def __init__(self):
        self.users = []

    async def create(self, user: UserEntity) -> UserEntity:
        """模擬建立使用者"""
        if user.id is None:
            user.id = uuid.uuid4()
        if user.created_at is None:
            user.created_at = datetime.utcnow()
        if user.updated_at is None:
            user.updated_at = datetime.utcnow()

        self.users.append(user)
        return user

    async def get_by_email(self, email: str) -> UserEntity | None:
        """根據 email 查詢使用者"""
        return next((u for u in self.users if u.email.lower() == email.lower()), None)

    async def get_by_id(self, user_id) -> UserEntity | None:
        """根據 ID 查詢使用者"""
        return next((u for u in self.users if str(u.id) == str(user_id)), None)

    async def update(self, user: UserEntity) -> UserEntity:
        """模擬更新使用者"""
        for i, u in enumerate(self.users):
            if str(u.id) == str(user.id):
                self.users[i] = user
                return user
        return user

    async def exists_by_email(self, email: str) -> bool:
        """檢查 email 是否存在"""
        return any(u.email.lower() == email.lower() for u in self.users)


# ==================== Test Cases ====================


@pytest.mark.asyncio
class TestRefreshTokenUseCase:
    """RefreshTokenUseCase 的單元測試"""

    @pytest.fixture
    def mock_repository(self):
        """提供 Mock Repository"""
        return MockUserRepository()

    @pytest.fixture
    def use_case(self, mock_repository):
        """提供 Use Case 實例"""
        return RefreshTokenUseCase(mock_repository)

    @pytest.fixture
    async def active_user(self, mock_repository):
        """建立一個啟用的測試使用者"""
        password = "SecurePass123!"
        hashed_password = get_password_hash(password)

        user = UserEntity(
            email="john@example.com",
            username="john_doe",
            password_hash=hashed_password,
            is_activate=True,
        )

        created_user = await mock_repository.create(user)
        return created_user

    @pytest.fixture
    async def inactive_user(self, mock_repository):
        """建立一個未啟用的測試使用者"""
        password = "SecurePass123!"
        hashed_password = get_password_hash(password)

        user = UserEntity(
            email="inactive@example.com",
            username="inactive_user",
            password_hash=hashed_password,
            is_active=False,  # 未啟用
        )

        created_user = await mock_repository.create(user)
        return created_user

    # ==================== 成功案例 ====================

    async def test_refresh_token_success(self, use_case, active_user):
        """測試成功刷新 Token"""
        # Arrange: 生成有效的 Refresh Token
        token_data = {
            "sub": str(active_user.email),
            "user_id": str(active_user.id),
        }
        refresh_token = create_refresh_token(data=token_data)

        input_dto = RefreshTokenInputDTO(refresh_token=refresh_token)

        # Act
        output_dto = await use_case.execute(input_dto)

        # Assert
        assert isinstance(output_dto, RefreshTokenOutputDTO)
        assert output_dto.access_token is not None
        assert output_dto.token_type == "bearer"

        # 驗證新的 Access Token 有效性
        payload = verify_token(output_dto.access_token, token_type="access")
        assert payload is not None
        assert payload["sub"] == str(active_user.email)
        assert payload["user_id"] == str(active_user.id)

    # ==================== 失敗案例 ====================

    async def test_refresh_token_invalid_token(self, use_case):
        """測試無效的 Refresh Token"""
        # Arrange
        input_dto = RefreshTokenInputDTO(refresh_token="invalid.token.here")

        # Act & Assert
        with pytest.raises(InvalidCredentialsError) as exc_info:
            await use_case.execute(input_dto)

        assert "帳號或密碼錯誤" in str(exc_info.value)

    async def test_refresh_token_user_not_found(self, use_case):
        """測試使用者不存在時刷新失敗"""
        # Arrange: 生成一個不存在使用者的 Token
        token_data = {
            "sub": "nonexistent@example.com",
            "user_id": str(uuid.uuid4()),
        }
        refresh_token = create_refresh_token(data=token_data)
        input_dto = RefreshTokenInputDTO(refresh_token=refresh_token)

        # Act & Assert
        with pytest.raises(InvalidCredentialsError) as exc_info:
            await use_case.execute(input_dto)

        assert "帳號或密碼錯誤" in str(exc_info.value)

    async def test_refresh_token_inactive_user(self, use_case, inactive_user):
        """測試未啟用使用者無法刷新 Token"""
        # Arrange
        token_data = {
            "sub": str(inactive_user.email),
            "user_id": str(inactive_user.id),
        }
        refresh_token = create_refresh_token(data=token_data)
        input_dto = RefreshTokenInputDTO(refresh_token=refresh_token)

        # Act & Assert
        with pytest.raises(InvalidCredentialsError) as exc_info:
            await use_case.execute(input_dto)

        assert "帳號或密碼錯誤" in str(exc_info.value)

    async def test_refresh_token_mismatched_user_id(self, use_case, active_user):
        """測試 Token 中的 user_id 與資料庫不匹配"""
        # Arrange: 生成 user_id 不匹配的 Token
        token_data = {
            "sub": str(active_user.email),
            "user_id": str(uuid.uuid4()),  # 不同的 user_id
        }
        refresh_token = create_refresh_token(data=token_data)
        input_dto = RefreshTokenInputDTO(refresh_token=refresh_token)

        # Act & Assert
        with pytest.raises(InvalidCredentialsError) as exc_info:
            await use_case.execute(input_dto)

        assert "帳號或密碼錯誤" in str(exc_info.value)

    async def test_refresh_token_with_access_token(self, use_case, active_user):
        """測試使用 Access Token 來刷新（應該失敗）"""
        # Arrange: 嘗試用 Access Token 而非 Refresh Token
        from core.security import create_access_token

        token_data = {
            "sub": str(active_user.email),
            "user_id": str(active_user.id),
        }
        access_token = create_access_token(data=token_data)  # 錯誤：使用 access token
        input_dto = RefreshTokenInputDTO(refresh_token=access_token)

        # Act & Assert
        with pytest.raises(InvalidCredentialsError) as exc_info:
            await use_case.execute(input_dto)

        assert "帳號或密碼錯誤" in str(exc_info.value)
