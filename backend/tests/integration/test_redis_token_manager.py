"""
Integration Tests for RedisTokenManager

測試範圍：
- 使用真實的 Redis 連接測試非同步操作
- 驗證 Token 的儲存、驗證、過期機制
- 測試雙重驗證流程的完整性
- 驗證 TTL 和自動清理功能

執行環境：
- 需要 Redis 服務運行在 localhost:6379
- 使用 DB 15 作為測試資料庫（避免影響開發環境）
- 測試前後自動清空測試資料庫

執行方式：
```bash
# 啟動 Redis（Docker）
docker run -d -p 6379:6379 redis:latest

# 執行測試
pytest tests/integration/test_redis_token_manager.py -v
```
"""

import pytest
import pytest_asyncio
import asyncio
from redis.asyncio import Redis
from infrastructure.redis.token_manager import RedisTokenManager


# ==================== Fixtures ====================


@pytest_asyncio.fixture
async def redis_client():
    """建立真實的 Redis 客戶端連接（測試用）"""
    redis = await Redis.from_url(
        "redis://localhost:6379/15",  # 使用 DB 15 作為測試資料庫
        encoding="utf-8",
        decode_responses=True
    )

    # 清空測試資料庫
    await redis.flushdb()

    yield redis

    # 測試結束後清理
    await redis.flushdb()
    await redis.close()


@pytest_asyncio.fixture
async def token_manager(redis_client):
    """建立 RedisTokenManager 實例"""
    return RedisTokenManager(redis_client=redis_client)


# ==================== Tests ====================


@pytest.mark.asyncio
class TestRedisTokenManagerIntegration:
    """RedisTokenManager 整合測試"""

    async def test_generate_token_uniqueness(self, token_manager):
        """測試生成的 token 具有唯一性"""
        tokens = set()
        for _ in range(100):
            token = token_manager.generate_token()
            assert token not in tokens, "Token 應該是唯一的"
            tokens.add(token)

        # 驗證 token 長度和格式
        for token in tokens:
            assert len(token) > 30, "Token 長度應大於 30 字元"
            assert isinstance(token, str), "Token 應為字串"

    async def test_store_and_retrieve_email_change_tokens(
        self,
        token_manager,
        redis_client
    ):
        """測試儲存和讀取信箱變更 tokens"""
        user_id = 123
        old_token = "test_old_token_abc123"
        new_token = "test_new_token_xyz789"
        new_email = "newemail@example.com"

        # 儲存 tokens
        await token_manager.store_email_change_tokens(
            user_id=user_id,
            old_token=old_token,
            new_token=new_token,
            new_email=new_email
        )

        # 驗證 Redis 中確實儲存了 5 個 keys
        keys = await redis_client.keys(f"email_change:{user_id}:*")
        assert len(keys) == 5, "應該儲存 5 個 keys"

        # 驗證每個 key 的值
        stored_old_token = await redis_client.get(f"email_change:{user_id}:old_token")
        assert stored_old_token == old_token

        stored_new_token = await redis_client.get(f"email_change:{user_id}:new_token")
        assert stored_new_token == new_token

        stored_email = await redis_client.get(f"email_change:{user_id}:pending_email")
        assert stored_email == new_email

        old_verified = await redis_client.get(f"email_change:{user_id}:old_verified")
        assert old_verified == "false"

        new_verified = await redis_client.get(f"email_change:{user_id}:new_verified")
        assert new_verified == "false"

    async def test_verify_token_success(self, token_manager):
        """測試驗證正確的 token"""
        user_id = 456
        old_token = token_manager.generate_token()
        new_token = token_manager.generate_token()

        await token_manager.store_email_change_tokens(
            user_id=user_id,
            old_token=old_token,
            new_token=new_token,
            new_email="test@example.com"
        )

        # 驗證舊信箱 token
        is_valid_old = await token_manager.verify_token(user_id, old_token, "old")
        assert is_valid_old is True

        # 驗證新信箱 token
        is_valid_new = await token_manager.verify_token(user_id, new_token, "new")
        assert is_valid_new is True

    async def test_verify_token_invalid(self, token_manager):
        """測試驗證錯誤的 token"""
        user_id = 789
        correct_token = "correct_token_abc"
        wrong_token = "wrong_token_xyz"

        await token_manager.store_email_change_tokens(
            user_id=user_id,
            old_token=correct_token,
            new_token="some_new_token",
            new_email="test@example.com"
        )

        # 使用錯誤的 token 驗證
        is_valid = await token_manager.verify_token(user_id, wrong_token, "old")
        assert is_valid is False

    async def test_verify_token_expired_user(self, token_manager):
        """測試不存在的使用者（token 已過期或不存在）"""
        non_existent_user_id = 99999
        any_token = "any_token"

        is_valid = await token_manager.verify_token(
            non_existent_user_id,
            any_token,
            "old"
        )
        assert is_valid is False

    async def test_mark_as_verified_and_check_both(self, token_manager):
        """測試標記已驗證並檢查雙重驗證狀態"""
        user_id = 111
        old_token = token_manager.generate_token()
        new_token = token_manager.generate_token()

        await token_manager.store_email_change_tokens(
            user_id=user_id,
            old_token=old_token,
            new_token=new_token,
            new_email="test@example.com"
        )

        # 初始狀態：兩個都未驗證
        both_verified = await token_manager.check_both_verified(user_id)
        assert both_verified is False

        # 標記舊信箱已驗證
        await token_manager.mark_as_verified(user_id, "old")

        # 檢查：只有舊信箱驗證
        both_verified = await token_manager.check_both_verified(user_id)
        assert both_verified is False

        # 標記新信箱已驗證
        await token_manager.mark_as_verified(user_id, "new")

        # 檢查：兩個都驗證完成
        both_verified = await token_manager.check_both_verified(user_id)
        assert both_verified is True

    async def test_get_pending_email(self, token_manager):
        """測試取得待變更的新信箱"""
        user_id = 222
        new_email = "pending@example.com"

        await token_manager.store_email_change_tokens(
            user_id=user_id,
            old_token="token1",
            new_token="token2",
            new_email=new_email
        )

        retrieved_email = await token_manager.get_pending_email(user_id)
        assert retrieved_email == new_email

    async def test_get_pending_email_not_exists(self, token_manager):
        """測試取得不存在的待變更信箱"""
        non_existent_user_id = 333

        retrieved_email = await token_manager.get_pending_email(non_existent_user_id)
        assert retrieved_email is None

    async def test_cleanup_email_change(self, token_manager, redis_client):
        """測試清理所有信箱變更相關資料"""
        user_id = 444

        await token_manager.store_email_change_tokens(
            user_id=user_id,
            old_token="token1",
            new_token="token2",
            new_email="cleanup@example.com"
        )

        # 確認資料已儲存
        keys_before = await redis_client.keys(f"email_change:{user_id}:*")
        assert len(keys_before) == 5

        # 執行清理
        await token_manager.cleanup_email_change(user_id)

        # 確認所有資料已刪除
        keys_after = await redis_client.keys(f"email_change:{user_id}:*")
        assert len(keys_after) == 0

    async def test_ttl_expiration(self, token_manager, redis_client):
        """測試 TTL 自動過期機制"""
        user_id = 555
        short_ttl = 2  # 2 秒

        await token_manager.store_email_change_tokens(
            user_id=user_id,
            old_token="token1",
            new_token="token2",
            new_email="ttl@example.com",
            ttl=short_ttl
        )

        # 立即檢查：資料應該存在
        keys_before = await redis_client.keys(f"email_change:{user_id}:*")
        assert len(keys_before) == 5

        # 等待 TTL 過期
        await asyncio.sleep(short_ttl + 1)

        # 檢查：資料應該自動刪除
        keys_after = await redis_client.keys(f"email_change:{user_id}:*")
        assert len(keys_after) == 0

    async def test_custom_ttl(self, token_manager, redis_client):
        """測試自訂 TTL"""
        user_id = 666
        custom_ttl = 3600  # 1 小時

        await token_manager.store_email_change_tokens(
            user_id=user_id,
            old_token="token1",
            new_token="token2",
            new_email="custom@example.com",
            ttl=custom_ttl
        )

        # 檢查 TTL 是否正確設定
        ttl = await redis_client.ttl(f"email_change:{user_id}:old_token")
        assert ttl > 3500  # 允許一些時間誤差
        assert ttl <= custom_ttl

    async def test_complete_email_change_workflow(self, token_manager):
        """測試完整的信箱變更工作流程"""
        user_id = 777
        new_email = "new@example.com"

        # Step 1: 生成 tokens
        old_token = token_manager.generate_token()
        new_token = token_manager.generate_token()

        # Step 2: 儲存到 Redis
        await token_manager.store_email_change_tokens(
            user_id=user_id,
            old_token=old_token,
            new_token=new_token,
            new_email=new_email
        )

        # Step 3: 模擬使用者點擊舊信箱驗證連結
        is_valid_old = await token_manager.verify_token(user_id, old_token, "old")
        assert is_valid_old is True

        await token_manager.mark_as_verified(user_id, "old")

        # Step 4: 檢查狀態（只有舊信箱驗證）
        both_verified = await token_manager.check_both_verified(user_id)
        assert both_verified is False

        # Step 5: 模擬使用者點擊新信箱驗證連結
        is_valid_new = await token_manager.verify_token(user_id, new_token, "new")
        assert is_valid_new is True

        await token_manager.mark_as_verified(user_id, "new")

        # Step 6: 檢查雙重驗證完成
        both_verified = await token_manager.check_both_verified(user_id)
        assert both_verified is True

        # Step 7: 取得待變更的新信箱
        pending_email = await token_manager.get_pending_email(user_id)
        assert pending_email == new_email

        # Step 8: 更新資料庫後清理 Redis（模擬）
        await token_manager.cleanup_email_change(user_id)

        # Step 9: 驗證清理成功
        pending_email_after = await token_manager.get_pending_email(user_id)
        assert pending_email_after is None

    async def test_concurrent_users(self, token_manager):
        """測試多個使用者同時進行信箱變更（併發測試）"""
        user_ids = [1001, 1002, 1003, 1004, 1005]

        # 同時為多個使用者儲存 tokens
        tasks = []
        for user_id in user_ids:
            task = token_manager.store_email_change_tokens(
                user_id=user_id,
                old_token=f"old_token_{user_id}",
                new_token=f"new_token_{user_id}",
                new_email=f"user{user_id}@example.com"
            )
            tasks.append(task)

        await asyncio.gather(*tasks)

        # 驗證每個使用者的資料都正確儲存且互不干擾
        for user_id in user_ids:
            pending_email = await token_manager.get_pending_email(user_id)
            assert pending_email == f"user{user_id}@example.com"

            is_valid = await token_manager.verify_token(
                user_id,
                f"old_token_{user_id}",
                "old"
            )
            assert is_valid is True

    async def test_mark_as_verified_preserves_ttl(
        self,
        token_manager,
        redis_client
    ):
        """測試標記為已驗證時保留原有的 TTL"""
        user_id = 888
        custom_ttl = 7200  # 2 小時

        await token_manager.store_email_change_tokens(
            user_id=user_id,
            old_token="token1",
            new_token="token2",
            new_email="ttl_test@example.com",
            ttl=custom_ttl
        )

        # 標記為已驗證
        await token_manager.mark_as_verified(user_id, "old")

        # 檢查 TTL 是否保留（允許一些時間誤差）
        ttl = await redis_client.ttl(f"email_change:{user_id}:old_verified")
        assert ttl > 7000  # 至少保留大部分的 TTL
        assert ttl <= custom_ttl

