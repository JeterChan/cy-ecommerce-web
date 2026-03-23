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
    DeleteAccountUseCase,
    UpdateProfileUseCase,
)
from modules.auth.application.dtos import RegisterRequestDTO, LoginRequestDTO
from modules.auth.application.dtos.update_profile_request import UpdateProfileRequest
from modules.auth.domain.entities import UserEntity
from core.exceptions import DuplicateEmailError, InvalidCredentialsError, UserNotRegisteredError, EmailNotVerifiedError, ValidationError

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
async def test_login_user_use_case_unverified(user_repo, password_hasher):
    # Arrange
    mock_user = MagicMock(spec=UserEntity)
    mock_user.email = "test@example.com"
    mock_user.password_hash = "hashed_pw"
    mock_user.is_verified = False
    user_repo.get_by_email.return_value = mock_user
    password_hasher.verify.return_value = True

    use_case = LoginUserUseCase(user_repo, password_hasher)
    data = LoginRequestDTO(email="test@example.com", password="password123")

    # Act & Assert
    with pytest.raises(EmailNotVerifiedError) as exc:
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
async def test_forgot_password_use_case_not_found(user_repo, token_manager):
    # Arrange
    user_repo.get_by_email.return_value = None
    use_case = ForgotPasswordUseCase(user_repo, token_manager)

    # Act & Assert
    with pytest.raises(UserNotRegisteredError):
        await use_case.execute("nonexistent@example.com")

@pytest.mark.asyncio
async def test_change_password_use_case_wrong_password(user_repo, password_hasher):
    # Arrange
    mock_user = MagicMock(spec=UserEntity)
    mock_user.password_hash = "hashed_pw"
    user_repo.get_by_id.return_value = mock_user
    password_hasher.verify.return_value = False

    use_case = ChangePasswordUseCase(user_repo, password_hasher)

    # Act & Assert
    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(uuid4(), "wrong", "new123")

@pytest.mark.asyncio
async def test_delete_account_use_case_success(user_repo, password_hasher):
    # Arrange
    user_id = uuid4()
    mock_user = MagicMock(spec=UserEntity)
    mock_user.id = user_id
    mock_user.email = "test@example.com"
    mock_user.password_hash = "hashed_pw"
    user_repo.get_by_id.return_value = mock_user
    password_hasher.verify.return_value = True

    use_case = DeleteAccountUseCase(user_repo, password_hasher)

    # Act
    await use_case.execute(user_id, "correct_password")

    # Assert
    assert mock_user.is_active is False
    assert mock_user.deleted_at is not None
    user_repo.update.assert_called_once()


# ── DeleteAccountUseCase (補強：使用 password_hasher) ──


@pytest.fixture
def password_hasher():
    return MagicMock()


@pytest.mark.asyncio
async def test_delete_account_success_with_email_prefix(user_repo, password_hasher):
    user_id = uuid4()
    mock_user = MagicMock(spec=UserEntity)
    mock_user.id = user_id
    mock_user.email = "test@example.com"
    mock_user.password_hash = "hashed_pw"
    user_repo.get_by_id.return_value = mock_user
    password_hasher.verify.return_value = True

    use_case = DeleteAccountUseCase(user_repo, password_hasher)
    await use_case.execute(user_id, "correct_password")

    password_hasher.verify.assert_called_once_with("correct_password", "hashed_pw")
    assert mock_user.is_active is False
    assert mock_user.deleted_at is not None
    # email 應加上 deleted_{id}_ 前綴
    assert mock_user.email == f"deleted_{user_id}_test@example.com"
    user_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_delete_account_wrong_password_raises(user_repo, password_hasher):
    user_id = uuid4()
    mock_user = MagicMock(spec=UserEntity)
    mock_user.id = user_id
    mock_user.email = "test@example.com"
    mock_user.password_hash = "hashed_pw"
    user_repo.get_by_id.return_value = mock_user
    password_hasher.verify.return_value = False

    use_case = DeleteAccountUseCase(user_repo, password_hasher)

    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(user_id, "wrong_password")

    # 不應修改使用者
    user_repo.update.assert_not_called()


# ── UpdateProfileUseCase ──


@pytest.mark.asyncio
async def test_update_profile_partial_update(user_repo):
    user_id = uuid4()
    mock_user = MagicMock(spec=UserEntity)
    mock_user.id = user_id
    mock_user.username = "original"
    mock_user.email = "test@example.com"
    mock_user.phone = None
    mock_user.address = None
    mock_user.created_at = datetime.now(timezone.utc)
    mock_user.updated_at = datetime.now(timezone.utc)
    mock_user.is_active = True
    mock_user.carrier_type = None
    mock_user.carrier_number = None
    mock_user.tax_id = None
    user_repo.get_by_id.return_value = mock_user
    user_repo.update.return_value = mock_user

    use_case = UpdateProfileUseCase(user_repo)
    request = UpdateProfileRequest(phone="0912345678")

    await use_case.execute(user_id, request)

    # phone 應被更新
    assert mock_user.phone == "0912345678"
    # username 不應被更新（request.username is None）
    assert mock_user.username == "original"
    user_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_profile_username_duplicate_raises(user_repo):
    user_id = uuid4()
    mock_user = MagicMock(spec=UserEntity)
    mock_user.id = user_id
    mock_user.username = "original"
    user_repo.get_by_id.return_value = mock_user
    user_repo.exists_by_username.return_value = True  # 已被使用

    use_case = UpdateProfileUseCase(user_repo)
    request = UpdateProfileRequest(username="taken_name")

    with pytest.raises(ValidationError, match="使用者名稱已存在"):
        await use_case.execute(user_id, request)

    user_repo.update.assert_not_called()
