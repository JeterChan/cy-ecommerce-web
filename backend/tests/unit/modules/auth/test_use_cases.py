import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone

from modules.auth.application.use_cases import (
    RegisterUserUseCase,
    LoginUserUseCase,
    VerifyEmailUseCase,
    ForgotPasswordUseCase,
    ResetPasswordUseCase,
    ChangePasswordUseCase,
    DeleteAccountUseCase
)
from modules.auth.application.dtos import RegisterRequestDTO, LoginRequestDTO
from modules.auth.domain.entities.UserEntity import UserEntity
from core.exceptions import DuplicateEmailError, InvalidCredentialsError

@pytest.fixture
def user_repo():
    return AsyncMock()

@pytest.fixture
def token_manager():
    mock = MagicMock()
    mock.generate_token = MagicMock(return_value="mock-token")
    mock.store_verification_token = AsyncMock()
    mock.get_user_id_by_verify_token = AsyncMock()
    mock.store_reset_token = AsyncMock()
    mock.get_user_id_by_reset_token = AsyncMock()
    return mock

@pytest.mark.asyncio
async def test_register_user_use_case_success(user_repo, token_manager):
    # Arrange
    user_repo.exists_by_email.return_value = False
    user_repo.create.side_effect = lambda u: u
    
    use_case = RegisterUserUseCase(user_repo, token_manager)
    data = RegisterRequestDTO(
        username="testuser",
        email="test@example.com",
        password="Password123!"
    )

    # Act
    with patch("modules.auth.application.use_cases.register.send_registration_verification") as mock_email_task:
        result = await use_case.execute(data)

    # Assert
    assert result.username == "testuser"
    user_repo.create.assert_called_once()
    token_manager.store_verification_token.assert_called_once()

@pytest.mark.asyncio
async def test_login_user_use_case_unverified(user_repo):
    # Arrange
    mock_user = MagicMock(spec=UserEntity)
    mock_user.email = "test@example.com"
    mock_user.is_verified = False
    user_repo.get_by_email.return_value = mock_user
    
    use_case = LoginUserUseCase(user_repo)
    data = LoginRequestDTO(email="test@example.com", password="password123")

    # Act & Assert
    with pytest.raises(InvalidCredentialsError) as exc:
        await use_case.execute(data)
    assert "請先完成信箱驗證" in str(exc.value)

@pytest.mark.asyncio
async def test_verify_email_use_case_success(user_repo, token_manager):
    # Arrange
    user_id = str(uuid4())
    token_manager.get_user_id_by_verify_token.return_value = user_id
    
    mock_user = MagicMock(spec=UserEntity)
    mock_user.id = user_id
    mock_user.email = "test@example.com"
    mock_user.is_verified = False
    
    user_repo.get_by_id.return_value = mock_user
    user_repo.update.return_value = mock_user
    
    use_case = VerifyEmailUseCase(user_repo, token_manager)

    # Act
    result = await use_case.execute("valid-token")

    # Assert
    assert result is True
    assert mock_user.is_verified is True
    user_repo.update.assert_called_once()

@pytest.mark.asyncio
async def test_forgot_password_use_case_success(user_repo, token_manager):
    # Arrange
    mock_user = MagicMock(spec=UserEntity)
    mock_user.id = uuid4()
    mock_user.email = "test@example.com"
    mock_user.username = "test"
    user_repo.get_by_email.return_value = mock_user
    
    use_case = ForgotPasswordUseCase(user_repo, token_manager)

    # Act
    with patch("modules.auth.application.use_cases.forgot_password.send_password_reset") as mock_email_task:
        result = await use_case.execute("test@example.com")

    # Assert
    assert result is True
    token_manager.store_reset_token.assert_called_once()

@pytest.mark.asyncio
async def test_change_password_use_case_wrong_password(user_repo):
    # Arrange
    mock_user = MagicMock(spec=UserEntity)
    mock_user.verify_password.return_value = False
    user_repo.get_by_id.return_value = mock_user
    
    use_case = ChangePasswordUseCase(user_repo)

    # Act & Assert
    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(uuid4(), "wrong", "new123")

@pytest.mark.asyncio
async def test_delete_account_use_case_success(user_repo):
    # Arrange
    user_id = uuid4()
    mock_user = MagicMock(spec=UserEntity)
    mock_user.id = user_id
    mock_user.email = "test@example.com"
    mock_user.verify_password.return_value = True
    user_repo.get_by_id.return_value = mock_user
    
    use_case = DeleteAccountUseCase(user_repo)

    # Act
    await use_case.execute(user_id, "correct_password")

    # Assert
    assert mock_user.is_active is False
    assert mock_user.deleted_at is not None
    user_repo.update.assert_called_once()
