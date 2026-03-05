"""
Unit Tests for RedisTokenManager

測試範圍：
- 測試 Token 生成
- 測試 Token 儲存與驗證
- 測試雙重驗證機制
- 測試資料清理
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys

# Mock redis.asyncio 模組以避免 import 錯誤
sys.modules['redis.asyncio'] = MagicMock()

from infrastructure.redis.token_manager import RedisTokenManager


class TestRedisTokenManager:
    """測試 RedisTokenManager"""

    @pytest.fixture
    def mock_redis(self):
        """建立 Mock Redis 客戶端"""
        redis = AsyncMock()
        return redis

    @pytest.fixture
    def token_manager(self, mock_redis):
        """建立 RedisTokenManager 實例"""
        return RedisTokenManager(redis_client=mock_redis)

    def test_initialization(self, token_manager):
        """測試初始化"""
        assert token_manager.default_ttl == 86400  # 24 小時

    def test_generate_token(self, token_manager):
        """測試生成 token"""
        token1 = token_manager.generate_token()
        token2 = token_manager.generate_token()

        # Token 應該是字串
        assert isinstance(token1, str)
        assert isinstance(token2, str)

        # Token 應該不同（隨機性）
        assert token1 != token2

        # Token 長度應該合理（URL-safe base64 編碼）
        assert len(token1) > 30
        assert len(token2) > 30


    async def test_store_email_change_tokens(self, token_manager, mock_redis):
        """測試儲存信箱變更 tokens"""
        user_id = 123
        old_token = "old_token_abc"
        new_token = "new_token_xyz"
        new_email = "new@example.com"

        await token_manager.store_email_change_tokens(
            user_id=user_id,
            old_token=old_token,
            new_token=new_token,
            new_email=new_email
        )

        # 驗證 Redis setex 被呼叫 5 次（5 個 key）
        assert mock_redis.setex.call_count == 5

        # 驗證儲存的 keys 和 values
        calls = mock_redis.setex.call_args_list
        stored_keys = [call[0][0] for call in calls]

        assert "email_change:123:old_token" in stored_keys
        assert "email_change:123:new_token" in stored_keys
        assert "email_change:123:pending_email" in stored_keys
        assert "email_change:123:old_verified" in stored_keys
        assert "email_change:123:new_verified" in stored_keys


    async def test_store_email_change_tokens_custom_ttl(self, token_manager, mock_redis):
        """測試使用自訂 TTL 儲存 tokens"""
        await token_manager.store_email_change_tokens(
            user_id=456,
            old_token="token1",
            new_token="token2",
            new_email="test@example.com",
            ttl=3600  # 1 小時
        )

        # 驗證所有 setex 使用自訂 TTL
        for call in mock_redis.setex.call_args_list:
            assert call[0][1] == 3600  # TTL 參數


    async def test_verify_token_success(self, token_manager, mock_redis):
        """測試驗證 token 成功"""
        user_id = 123
        token = "test_token_abc"

        # Mock Redis 返回儲存的 token
        mock_redis.get.return_value = token.encode()

        result = await token_manager.verify_token(
            user_id=user_id,
            token=token,
            token_type="old"
        )

        assert result is True
        mock_redis.get.assert_called_once_with("email_change:123:old_token")


    async def test_verify_token_invalid(self, token_manager, mock_redis):
        """測試驗證 token 失敗（token 不符）"""
        user_id = 123
        stored_token = "correct_token"
        provided_token = "wrong_token"

        # Mock Redis 返回不同的 token
        mock_redis.get.return_value = stored_token.encode()

        result = await token_manager.verify_token(
            user_id=user_id,
            token=provided_token,
            token_type="old"
        )

        assert result is False


    async def test_verify_token_expired(self, token_manager, mock_redis):
        """測試驗證 token 失敗（token 已過期）"""
        user_id = 123

        # Mock Redis 返回 None（token 不存在或已過期）
        mock_redis.get.return_value = None

        result = await token_manager.verify_token(
            user_id=user_id,
            token="any_token",
            token_type="new"
        )

        assert result is False


    async def test_mark_as_verified(self, token_manager, mock_redis):
        """測試標記為已驗證"""
        user_id = 123

        # Mock Redis ttl 返回值
        mock_redis.ttl.return_value = 3600

        await token_manager.mark_as_verified(
            user_id=user_id,
            token_type="old"
        )

        # 驗證 ttl 被呼叫
        mock_redis.ttl.assert_called_once_with("email_change:123:old_verified")

        # 驗證 setex 被呼叫，值為 "true"
        mock_redis.setex.assert_called_once_with(
            "email_change:123:old_verified",
            3600,
            "true"
        )


    async def test_mark_as_verified_expired_ttl(self, token_manager, mock_redis):
        """測試標記為已驗證（TTL 已過期，使用預設值）"""
        user_id = 123

        # Mock Redis ttl 返回 -1（key 不存在）
        mock_redis.ttl.return_value = -1

        await token_manager.mark_as_verified(
            user_id=user_id,
            token_type="new"
        )

        # 驗證使用預設 TTL
        mock_redis.setex.assert_called_once_with(
            "email_change:123:new_verified",
            86400,  # default_ttl
            "true"
        )


    async def test_check_both_verified_true(self, token_manager, mock_redis):
        """測試檢查兩個信箱都已驗證"""
        user_id = 123

        # Mock Redis 返回兩個都已驗證
        mock_redis.get.side_effect = [b"true", b"true"]

        result = await token_manager.check_both_verified(user_id)

        assert result is True
        assert mock_redis.get.call_count == 2


    async def test_check_both_verified_only_old(self, token_manager, mock_redis):
        """測試只有舊信箱已驗證"""
        user_id = 123

        # Mock Redis 返回：舊信箱驗證，新信箱未驗證
        mock_redis.get.side_effect = [b"true", b"false"]

        result = await token_manager.check_both_verified(user_id)

        assert result is False


    async def test_check_both_verified_only_new(self, token_manager, mock_redis):
        """測試只有新信箱已驗證"""
        user_id = 123

        # Mock Redis 返回：舊信箱未驗證，新信箱驗證
        mock_redis.get.side_effect = [b"false", b"true"]

        result = await token_manager.check_both_verified(user_id)

        assert result is False


    async def test_check_both_verified_none(self, token_manager, mock_redis):
        """測試兩個信箱都未驗證"""
        user_id = 123

        # Mock Redis 返回兩個都未驗證
        mock_redis.get.side_effect = [b"false", b"false"]

        result = await token_manager.check_both_verified(user_id)

        assert result is False


    async def test_check_both_verified_missing_keys(self, token_manager, mock_redis):
        """測試 key 不存在的情況"""
        user_id = 123

        # Mock Redis 返回 None（key 不存在）
        mock_redis.get.side_effect = [None, None]

        result = await token_manager.check_both_verified(user_id)

        assert result is False


    async def test_get_pending_email(self, token_manager, mock_redis):
        """測試取得待變更的新信箱"""
        user_id = 123
        new_email = "new@example.com"

        # Mock Redis 返回新信箱
        mock_redis.get.return_value = new_email.encode()

        result = await token_manager.get_pending_email(user_id)

        assert result == new_email
        mock_redis.get.assert_called_once_with("email_change:123:pending_email")


    async def test_get_pending_email_not_found(self, token_manager, mock_redis):
        """測試取得待變更信箱（不存在）"""
        user_id = 123

        # Mock Redis 返回 None
        mock_redis.get.return_value = None

        result = await token_manager.get_pending_email(user_id)

        assert result is None


    async def test_cleanup_email_change(self, token_manager, mock_redis):
        """測試清理所有信箱變更資料"""
        user_id = 123

        await token_manager.cleanup_email_change(user_id)

        # 驗證 delete 被呼叫，並包含所有 5 個 keys
        mock_redis.delete.assert_called_once()
        deleted_keys = mock_redis.delete.call_args[0]

        assert len(deleted_keys) == 5
        assert "email_change:123:old_token" in deleted_keys
        assert "email_change:123:new_token" in deleted_keys
        assert "email_change:123:pending_email" in deleted_keys
        assert "email_change:123:old_verified" in deleted_keys
        assert "email_change:123:new_verified" in deleted_keys

