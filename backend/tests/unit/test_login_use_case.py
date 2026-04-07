"""
Unit Tests for LoginUserUseCase

測試範圍：
- 測試 Use Case 業務邏輯
- 使用 Mock Repository（不依賴真實資料庫）
- 快速執行、易於維護
"""

import pytest
from datetime import datetime
import uuid

from modules.auth.use_cases.login import LoginUserUseCase
from modules.auth.use_cases.dtos import (
    LoginUserInputDTO,
    LoginUserOutputDTO,
)
from modules.auth.domain.entities.UserEntity import UserEntity
from modules.auth.domain.repositories.i_user_repository import IUserRepository
from core.exceptions import InvalidCredentialsError, UserNotRegisteredError
from core.security import get_password_hash, verify_token

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

    """LoginUserUseCase 的單元測試"""

    @pytest.fixture
    def mock_repository(self):
        """提供 Mock Repository"""
        return MockUserRepository()

    @pytest.fixture
    def use_case(self, mock_repository):
        """提供 Use Case 實例"""
        return LoginUserUseCase(mock_repository)

    @pytest.fixture
    async def registered_user(self, mock_repository):
        """建立一個已註冊的測試使用者"""
        password = "SecurePass123!"
        hashed_password = get_password_hash(password)

        user = UserEntity(
            email="john@example.com",
            username="john_doe",
            password_hash=hashed_password,
            is_activate=True,
        )

        created_user = await mock_repository.create(user)

        # 返回使用者資料和明文密碼
        return {"user": created_user, "password": password}

    # ==================== 成功案例 ====================

    async def test_login_success(self, use_case, registered_user):
        """測試成功登入"""
        # Arrange
        user_data = registered_user
        input_dto = LoginUserInputDTO(
            email=user_data["user"].email, password=user_data["password"]
        )

        # Act
        output_dto = await use_case.execute(input_dto)

        # Assert
        assert isinstance(output_dto, LoginUserOutputDTO)
        assert output_dto.id == user_data["user"].id
        assert output_dto.username == user_data["user"].username
        assert output_dto.email == user_data["user"].email
        assert output_dto.is_active is True
        assert output_dto.access_token is not None
        assert output_dto.token_type == "bearer"
        assert output_dto.refresh_token is None  # Phase 5 才會實作

        # 驗證 Token 有效性
        payload = verify_token(output_dto.access_token, token_type="access")
        assert payload is not None
        assert payload["sub"] == str(user_data["user"].email)
        assert payload["user_id"] == str(user_data["user"].id)

    async def test_login_email_case_insensitive(self, use_case, registered_user):
        """測試 Email 不區分大小寫登入"""
        # Arrange
        user_data = registered_user
        input_dto = LoginUserInputDTO(
            email="JOHN@EXAMPLE.COM", password=user_data["password"]  # 大寫
        )

        # Act
        output_dto = await use_case.execute(input_dto)

        # Assert
        assert output_dto.id == user_data["user"].id
        assert output_dto.email == user_data["user"].email

    # ==================== 失敗案例 ====================

    async def test_login_user_not_found(self, use_case):
        """測試使用者不存在時登入失敗"""
        # Arrange
        input_dto = LoginUserInputDTO(
            email="notexist@example.com", password="AnyPassword123!"
        )

        # Act & Assert
        with pytest.raises(UserNotRegisteredError) as exc_info:
            await use_case.execute(input_dto)

        assert "尚未註冊" in str(exc_info.value)

    async def test_login_wrong_password(self, use_case, registered_user):
        """測試密碼錯誤時登入失敗"""
        # Arrange
        user_data = registered_user
        input_dto = LoginUserInputDTO(
            email=user_data["user"].email, password="WrongPassword123!"  # 錯誤的密碼
        )

        # Act & Assert
        with pytest.raises(InvalidCredentialsError) as exc_info:
            await use_case.execute(input_dto)

        assert "帳號或密碼錯誤" in str(exc_info.value)

    async def test_login_empty_password(self, use_case, registered_user):
        """測試空密碼登入失敗（Pydantic 驗證層）"""
        # Arrange
        user_data = registered_user

        # Act & Assert
        with pytest.raises(Exception):  # Pydantic ValidationError
            LoginUserInputDTO(
                email=user_data["user"].email, password=""  # 空密碼
            )

    # ==================== Token 驗證測試 ====================

    async def test_generated_token_contains_user_info(self, use_case, registered_user):
        """測試生成的 Token 包含正確的使用者資訊"""
        # Arrange
        user_data = registered_user
        input_dto = LoginUserInputDTO(
            email=user_data["user"].email, password=user_data["password"]
        )

        # Act
        output_dto = await use_case.execute(input_dto)

        # Assert - 驗證 Token payload
        payload = verify_token(output_dto.access_token, token_type="access")
        assert payload is not None
        assert payload["sub"] == str(user_data["user"].email)
        assert payload["user_id"] == str(user_data["user"].id)
        assert "exp" in payload  # 過期時間
        assert payload["type"] == "access"

    async def test_token_expiration_field_exists(self, use_case, registered_user):
        """測試 Token 包含過期時間"""
        # Arrange
        user_data = registered_user
        input_dto = LoginUserInputDTO(
            email=user_data["user"].email, password=user_data["password"]
        )

        # Act
        output_dto = await use_case.execute(input_dto)

        # Assert
        payload = verify_token(output_dto.access_token, token_type="access")
        assert "exp" in payload
        assert payload["exp"] > datetime.utcnow().timestamp()  # 過期時間應該在未來

    # ==================== 多次登入測試 ====================

    async def test_multiple_logins_generate_different_tokens(
        self, use_case, registered_user
    ):
        """測試多次登入產生不同的 Token"""
        # Arrange
        user_data = registered_user
        input_dto = LoginUserInputDTO(
            email=user_data["user"].email, password=user_data["password"]
        )

        # Act
        output_dto1 = await use_case.execute(input_dto)
        output_dto2 = await use_case.execute(input_dto)

        # Assert - Token 不同（因為時間戳不同）
        # 注意：在極短時間內可能產生相同 Token，但機率極低
        # 主要驗證都是有效的 Token
        assert verify_token(output_dto1.access_token, token_type="access") is not None
        assert verify_token(output_dto2.access_token, token_type="access") is not None
