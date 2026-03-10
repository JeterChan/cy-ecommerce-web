import secrets
from redis.asyncio import Redis
from typing import Optional

class RedisTokenManager:
    """用於 Auth 流程中的 Token 管理 (Email 驗證, 密碼重設, 信箱變更)"""
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.default_ttl = 86400  # 24 小時

    def generate_token(self) -> str:
        """生成 32 字元的安全隨機 token"""
        return secrets.token_urlsafe(32)

    # --- 註冊驗證與密碼重設 (New) ---

    async def store_verification_token(self, user_id: str, token: str, ttl: int = 86400) -> None:
        """儲存註冊驗證 Token (預設 24h)"""
        key = f"auth:verify:{token}"
        await self.redis.setex(key, ttl, user_id)

    async def get_user_id_by_verify_token(self, token: str) -> Optional[str]:
        """透過驗證 Token 取得 User ID 並刪除 (單次使用)"""
        key = f"auth:verify:{token}"
        user_id = await self.redis.get(key)
        if user_id:
            if isinstance(user_id, bytes):
                user_id = user_id.decode()
            await self.redis.delete(key)
            return user_id
        return None

    async def store_reset_token(self, user_id: str, token: str, ttl: int = 3600) -> None:
        """儲存密碼重設 Token (預設 1h)"""
        key = f"auth:reset:{token}"
        await self.redis.setex(key, ttl, user_id)

    async def get_user_id_by_reset_token(self, token: str) -> Optional[str]:
        """透過重設 Token 取得 User ID 並刪除 (單次使用)"""
        key = f"auth:reset:{token}"
        user_id = await self.redis.get(key)
        if user_id:
            if isinstance(user_id, bytes):
                user_id = user_id.decode()
            await self.redis.delete(key)
            return user_id
        return None

    # --- 原有的信箱變更邏輯 (保留) ---

    async def store_email_change_tokens(
        self,
        user_id: str,
        old_token: str,
        new_token: str,
        new_email: str,
        ttl: int | None = None
    ) -> None:
        ttl = ttl or self.default_ttl
        prefix = f"email_change:{user_id}"
        await self.redis.setex(f"{prefix}:old_token", ttl, old_token)
        await self.redis.setex(f"{prefix}:new_token", ttl, new_token)
        await self.redis.setex(f"{prefix}:pending_email", ttl, new_email)
        await self.redis.setex(f"{prefix}:old_verified", ttl, "false")
        await self.redis.setex(f"{prefix}:new_verified", ttl, "false")

    async def verify_token(self, user_id: str, token: str, token_type: str) -> bool:
        prefix = f"email_change:{user_id}"
        stored_token = await self.redis.get(f"{prefix}:{token_type}_token")
        if not stored_token:
            return False
        if isinstance(stored_token, bytes):
            stored_token = stored_token.decode()
        return stored_token == token

    async def mark_as_verified(self, user_id: str, token_type: str) -> None:
        key = f"email_change:{user_id}:{token_type}_verified"
        ttl = await self.redis.ttl(key)
        await self.redis.setex(key, ttl if ttl > 0 else self.default_ttl, "true")

    async def check_both_verified(self, user_id: str) -> bool:
        prefix = f"email_change:{user_id}"
        old_verified = await self.redis.get(f"{prefix}:old_verified")
        new_verified = await self.redis.get(f"{prefix}:new_verified")
        if isinstance(old_verified, bytes):
            old_verified = old_verified.decode()
        if isinstance(new_verified, bytes):
            new_verified = new_verified.decode()
        return old_verified == "true" and new_verified == "true"

    async def get_pending_email(self, user_id: str) -> str | None:
        key = f"email_change:{user_id}:pending_email"
        email = await self.redis.get(key)
        if not email:
            return None
        if isinstance(email, bytes):
            email = email.decode()
        return email

    async def cleanup_email_change(self, user_id: str) -> None:
        prefix = f"email_change:{user_id}"
        keys = [
            f"{prefix}:old_token",
            f"{prefix}:new_token",
            f"{prefix}:pending_email",
            f"{prefix}:old_verified",
            f"{prefix}:new_verified",
        ]
        await self.redis.delete(*keys)
