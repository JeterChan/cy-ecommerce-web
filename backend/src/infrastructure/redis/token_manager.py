import secrets
from redis.asyncio import Redis

class RedisTokenManager:
    """用於 Email 驗證流程"""
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.default_ttl = 86400

    def generate_token(self) -> str:
        """生成32字元的安全隨機 token"""
        return secrets.token_urlsafe(32)

    async def store_email_change_tokens(
        self,
        user_id: str,
        old_token: str,
        new_token: str,
        new_email: str,
        ttl: int | None = None
    ) -> None:
        """
        儲存信箱變更所需的所有資料
        :param user_id:
        :param old_token: 舊信箱驗證 token
        :param new_token: 新信箱驗證 token
        :param new_email: 帶變更的新信箱
        :param ttl: 過期時間 (秒), 預設 24 小時
        """
        ttl = ttl or self.default_ttl
        prefix = f"email_change:{user_id}"

        await self.redis.setex(f"{prefix}:old_token",ttl,old_token)
        await self.redis.setex(f"{prefix}:new_token", ttl, new_token)

        await self.redis.setex(f"{prefix}:pending_email", ttl, new_email)

        await self.redis.setex(f"{prefix}:old_verified", ttl, "false")
        await self.redis.setex(f"{prefix}:new_verified", ttl, "false")

    async def verify_token(
        self,
        user_id: str,
        token: str,
        token_type: str # "old" or "new"
    ) -> bool:
        """
        驗證 token 是否正確
        :return:
            True: token 正確
            False: token 錯誤或已過期
        """
        prefix = f"email_change:{user_id}"
        stored_token = await self.redis.get(f"{prefix}:{token_type}_token")

        if not stored_token:
            return False # Token 不存在或過期

        if isinstance(stored_token, bytes):
            stored_token = stored_token.decode()
        return stored_token == token

    async def mark_as_verified(
        self,
        user_id: str,
        token_type: str
    ) -> None:
        """標記某個信箱已驗證"""
        key = f"email_change:{user_id}:{token_type}_verified"
        ttl = await self.redis.ttl(key)
        await self.redis.setex(key, ttl if ttl > 0 else self.default_ttl, "true")

    async def check_both_verified(self, user_id: str) -> bool:
        """檢查兩個信箱是否都已驗證"""
        prefix = f"email_change:{user_id}"
        old_verified = await self.redis.get(f"{prefix}:old_verified")
        new_verified = await self.redis.get(f"{prefix}:new_verified")

        if isinstance(old_verified, bytes):
            old_verified = old_verified.decode()
        if isinstance(new_verified, bytes):
            new_verified = new_verified.decode()

        return (
            old_verified == "true" and
            new_verified == "true"
        )

    async def get_pending_email(self, user_id: str) -> str | None:
        key = f"email_change:{user_id}:pending_email"
        email = await self.redis.get(key)
        if not email:
            return None
        if isinstance(email, bytes):
            email = email.decode()
        return email

    async def cleanup_email_change(self, user_id: str) -> None:
        """清理所有信箱變更相關的 Redis 資料"""
        prefix = f"email_change:{user_id}"
        keys = [
            f"{prefix}:old_token",
            f"{prefix}:new_token",
            f"{prefix}:pending_email",
            f"{prefix}:old_verified",
            f"{prefix}:new_verified",
        ]
        await self.redis.delete(*keys)