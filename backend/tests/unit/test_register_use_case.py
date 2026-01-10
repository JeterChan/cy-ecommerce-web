"""
Unit Tests for RegisterUserUseCase

測試範圍：
- 測試 Use Case 業務邏輯
- 使用 Mock Repository（不依賴真實資料庫）
- 快速執行、易於維護
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock
import uuid

from src.modules.auth.use_cases.register import RegisterUserUseCase
from src.modules.auth.use_cases.dtos import (
    RegisterUserInputDTO,
    RegisterUserOutputDTO,
)
from src.modules.auth.domain.entities import UserEntity
from src.modules.auth.domain.repositories.i_user_repository import IUserRepository
from src.core.exceptions import DuplicateEmailError


# ==================== Mock Repository ====================

class MockUserRepository(IUserRepository):
    """Mock User Repository for Unit Testing"""

    def __init__(self):
        self.users = []

    async def create(self, user: UserEntity) -> UserEntity:
        """模擬建立使用者"""
        # 檢查電子郵件是否已存在
        if any(u.email == user.email for u in self.users):
            raise DuplicateEmailError(f"Email {user.email} already exists")

        # 設定 ID 和時間戳（如果沒有的話）
        if user.id is None:
            user.id = uuid.uuid4()
        if user.created_at is None:
            user.created_at = datetime.utcnow()
        if user.updated_at is None:
            user.updated_at = datetime.utcnow()

        self.users.append(user)
        return user

    async def get_by_id(self, user_id: int) -> UserEntity | None:
        return next((u for u in self.users if u.id == user_id), None)

    async def get_by_email(self, email: str) -> UserEntity | None:
        return next((u for u in self.users if u.email == email), None)

    async def get_by_username(self, username: str) -> UserEntity | None:
        return next((u for u in self.users if u.username == username), None)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[UserEntity]:
        return self.users[skip : skip + limit]

    async def update(self, user_id: int, user_data: dict) -> UserEntity:
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        for key, value in user_data.items():
            setattr(user, key, value)
        return user

    async def delete(self, user_id: int) -> bool:
        user = await self.get_by_id(user_id)
        if user:
            self.users.remove(user)
            return True
        return False

    async def exists_by_email(self, email: str) -> bool:
        return any(u.email == email for u in self.users)


# ==================== Test Cases ====================

@pytest.mark.asyncio
class TestRegisterUserUseCase:
    """RegisterUserUseCase 的單元測試"""

    @pytest.fixture
    def mock_repository(self):
        """提供 Mock Repository"""
        return MockUserRepository()

    @pytest.fixture
    def use_case(self, mock_repository):
        """提供 Use Case 實例"""
        return RegisterUserUseCase(mock_repository)

    # ==================== 成功案例 ====================

    async def test_register_user_success(self, use_case, mock_repository):
        """測試成功註冊使用者"""
        # Arrange
        input_dto = RegisterUserInputDTO(
            username="john_doe",
            email="john@example.com",
            password="SecurePass123!",
        )

        # Act
        output_dto = await use_case.execute(input_dto)

        # Assert
        assert output_dto.id is not None  # UUID 自動生成
        assert output_dto.username == "john_doe"
        assert output_dto.email == "john@example.com"
        assert output_dto.is_active is True
        assert output_dto.created_at is not None

        # 驗證 Repository 中確實有使用者
        assert len(mock_repository.users) == 1
        assert mock_repository.users[0].username == "john_doe"

    async def test_register_user_password_is_hashed(self, use_case, mock_repository):
        """測試密碼已被雜湊處理"""
        # Arrange
        plain_password = "MySecretPass123!"
        input_dto = RegisterUserInputDTO(
            username="alice",
            email="alice@example.com",
            password=plain_password,
        )

        # Act
        output_dto = await use_case.execute(input_dto)

        # Assert
        created_user = mock_repository.users[0]
        assert created_user.password_hash != plain_password
        assert created_user.password_hash.startswith("$2b$")  # Bcrypt 前綴

    async def test_register_multiple_users(self, use_case, mock_repository):
        """測試註冊多個使用者"""
        # Arrange
        users_data = [
            ("alice", "alice@example.com", "AlicePass123!"),
            ("bob", "bob@example.com", "BobPass123!"),
            ("charlie", "charlie@example.com", "CharliePass123!"),
        ]

        # Act
        results = []
        for username, email, password in users_data:
            input_dto = RegisterUserInputDTO(
                username=username, email=email, password=password
            )
            output_dto = await use_case.execute(input_dto)
            results.append(output_dto)

        # Assert
        assert len(results) == 3
        assert len(mock_repository.users) == 3
        # 檢查每個使用者都有 UUID
        for result in results:
            assert result.id is not None

    # ==================== 錯誤案例 ====================

    async def test_register_user_duplicate_email(self, use_case, mock_repository):
        """測試重複的電子郵件"""
        # Arrange
        email = "duplicate@example.com"

        # 先註冊第一個使用者
        first_input = RegisterUserInputDTO(
            username="user1", email=email, password="FirstPass123!"
        )
        await use_case.execute(first_input)

        # Act & Assert
        # 嘗試用相同電子郵件註冊第二個使用者
        second_input = RegisterUserInputDTO(
            username="user2", email=email, password="SecondPass123!"
        )

        with pytest.raises(DuplicateEmailError) as exc_info:
            await use_case.execute(second_input)

        assert email in str(exc_info.value)
        assert "already registered" in str(exc_info.value)

        # 驗證只建立了一個使用者
        assert len(mock_repository.users) == 1

    async def test_register_user_invalid_username_too_short(self, use_case):
        """測試使用者名稱過短（DTO 驗證）"""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            RegisterUserInputDTO(
                username="ab",  # 只有 2 個字元
                email="test@example.com",
                password="TestPass123!",
            )

        assert "at least 3 characters" in str(exc_info.value)

    async def test_register_user_invalid_email_format(self, use_case):
        """測試無效的電子郵件格式（DTO 驗證）"""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            RegisterUserInputDTO(
                username="testuser",
                email="invalid-email",  # 無效格式
                password="TestPass123!",
            )

        assert "email" in str(exc_info.value).lower()

    async def test_register_user_weak_password_no_uppercase(self, use_case):
        """測試弱密碼（缺少大寫字母）"""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            RegisterUserInputDTO(
                username="testuser",
                email="test@example.com",
                password="weakpass123!",  # 沒有大寫字母
            )

        assert "uppercase" in str(exc_info.value).lower()

    async def test_register_user_weak_password_no_digit(self, use_case):
        """測試弱密碼（缺少數字）"""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            RegisterUserInputDTO(
                username="testuser",
                email="test@example.com",
                password="WeakPassword!",  # 沒有數字
            )

        assert "digit" in str(exc_info.value).lower()

    async def test_register_user_invalid_username_special_chars(self, use_case):
        """測試使用者名稱包含特殊字元"""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            RegisterUserInputDTO(
                username="user@name!",  # 包含特殊字元
                email="test@example.com",
                password="TestPass123!",
            )

        assert "letters, numbers" in str(exc_info.value)

    # ==================== Edge Cases ====================

    async def test_register_user_username_normalized_to_lowercase(self, use_case, mock_repository):
        """測試使用者名稱自動轉為小寫"""
        # Arrange
        input_dto = RegisterUserInputDTO(
            username="JohnDoe",  # 混合大小寫
            email="john@example.com",
            password="TestPass123!",
        )

        # Act
        output_dto = await use_case.execute(input_dto)

        # Assert
        assert output_dto.username == "johndoe"  # 應轉為小寫
        assert mock_repository.users[0].username == "johndoe"

    async def test_register_user_default_values(self, use_case, mock_repository):
        """測試預設值設定正確"""
        # Arrange
        input_dto = RegisterUserInputDTO(
            username="testuser",
            email="test@example.com",
            password="TestPass123!",
        )

        # Act
        output_dto = await use_case.execute(input_dto)

        # Assert
        assert output_dto.is_active is True  # 預設應啟用

    async def test_register_user_password_minimum_length(self, use_case):
        """測試密碼最小長度（8 個字元）"""
        # Act & Assert - 7 個字元應失敗
        with pytest.raises(ValueError):
            RegisterUserInputDTO(
                username="testuser",
                email="test@example.com",
                password="Pass12!",  # 只有 7 個字元
            )

        # 8 個字元應成功
        valid_dto = RegisterUserInputDTO(
            username="testuser",
            email="test@example.com",
            password="Pass123!",  # 8 個字元
        )
        assert valid_dto.password == "Pass123!"


# ==================== DTO Validation Tests ====================

class TestRegisterUserInputDTO:
    """RegisterUserInputDTO 的驗證測試"""

    def test_valid_input(self):
        """測試有效的輸入"""
        dto = RegisterUserInputDTO(
            username="valid_user",
            email="valid@example.com",
            password="ValidPass123!",
        )

        assert dto.username == "valid_user"
        assert dto.email == "valid@example.com"
        assert dto.password == "ValidPass123!"

    def test_username_with_underscore(self):
        """測試使用者名稱可包含底線"""
        dto = RegisterUserInputDTO(
            username="user_name_123",
            email="test@example.com",
            password="TestPass123!",
        )

        assert dto.username == "user_name_123"

    def test_username_with_hyphen(self):
        """測試使用者名稱可包含連字號"""
        dto = RegisterUserInputDTO(
            username="user-name-123",
            email="test@example.com",
            password="TestPass123!",
        )

        assert dto.username == "user-name-123"

    def test_username_cannot_start_with_underscore(self):
        """測試使用者名稱不能以底線開頭"""
        with pytest.raises(ValueError) as exc_info:
            RegisterUserInputDTO(
                username="_username",
                email="test@example.com",
                password="TestPass123!",
            )

        assert "cannot start" in str(exc_info.value)

    def test_username_cannot_end_with_hyphen(self):
        """測試使用者名稱不能以連字號結尾"""
        with pytest.raises(ValueError) as exc_info:
            RegisterUserInputDTO(
                username="username-",
                email="test@example.com",
                password="TestPass123!",
            )

        assert "cannot" in str(exc_info.value) and "end" in str(exc_info.value)

    def test_password_with_special_characters(self):
        """測試密碼可包含特殊字元"""
        dto = RegisterUserInputDTO(
            username="testuser",
            email="test@example.com",
            password="P@ssw0rd!#$%",
        )

        assert dto.password == "P@ssw0rd!#$%"

