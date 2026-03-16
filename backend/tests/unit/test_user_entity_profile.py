"""
Unit Tests for UserEntity Profile Fields

測試範圍：
- 測試新增的個人檔案欄位
- 測試軟刪除功能
- 驗證業務邏輯方法
"""

from datetime import datetime, timezone
import uuid

from modules.auth.domain.entities.UserEntity import UserEntity


class TestUserEntityProfileFields:
    """測試 UserEntity 的個人檔案欄位"""

    def test_create_user_with_profile_fields(self):
        """測試建立包含個人檔案欄位的使用者"""
        user = UserEntity(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            is_active=True,
            display_name="Test User",
            phone_number="+886912345678",
            avatar_url="https://example.com/avatar.jpg",
            bio="這是我的個人介紹",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        assert user.display_name == "Test User"
        assert user.phone_number == "+886912345678"
        assert user.avatar_url == "https://example.com/avatar.jpg"
        assert user.bio == "這是我的個人介紹"
        assert user.deleted_at is None

    def test_create_user_without_profile_fields(self):
        """測試建立不包含個人檔案欄位的使用者（使用預設值）"""
        user = UserEntity(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        assert user.display_name is None
        assert user.phone_number is None
        assert user.avatar_url is None
        assert user.bio is None
        assert user.deleted_at is None

    def test_soft_delete_user(self):
        """測試軟刪除使用者"""
        user = UserEntity(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        # 執行軟刪除
        user.soft_delete()

        # 驗證軟刪除結果
        assert user.deleted_at is not None
        assert user.is_active is False
        assert isinstance(user.deleted_at, datetime)

    def test_is_deleted_method(self):
        """測試 is_deleted 方法"""
        user = UserEntity(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        # 初始狀態：未刪除
        assert user.is_deleted() is False

        # 執行軟刪除
        user.soft_delete()

        # 刪除後狀態：已刪除
        assert user.is_deleted() is True

    def test_soft_delete_deactivates_user(self):
        """測試軟刪除會同時停用使用者"""
        user = UserEntity(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        assert user.is_active is True

        user.soft_delete()

        assert user.is_active is False
        assert user.is_deleted() is True

    def test_existing_activate_deactivate_methods(self):
        """測試現有的 activate 和 deactivate 方法仍然正常運作"""
        user = UserEntity(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            is_active=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        # 測試啟用
        user.activate()
        assert user.is_active is True

        # 測試停用
        user.deactivate()
        assert user.is_active is False

    def test_backward_compatibility_with_existing_fields(self):
        """測試向後相容性：現有欄位（phone, address, carrier_type 等）仍然可用"""
        user = UserEntity(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            phone="0912345678",
            address="台北市信義區",
            carrier_type="MOBILE",
            carrier_number="/ABC123",
            tax_id="12345678",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        assert user.phone == "0912345678"
        assert user.address == "台北市信義區"
        assert user.carrier_type == "MOBILE"
        assert user.carrier_number == "/ABC123"
        assert user.tax_id == "12345678"

