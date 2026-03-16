"""驗證電子郵件變更 Use Case"""
from modules.auth.domain.repository import IUserRepository
from modules.auth.application.dtos import VerifyEmailChangeRequest
from infrastructure.redis.token_manager import RedisTokenManager
from core.exceptions import ValidationError


class VerifyEmailChangeUseCase:
    """
    驗證 Email 變更 Use Case

    流程：
    1. 驗證 token 正確性
    2. 標記該端已驗證
    3. 若新舊 Email 兩端均已驗證，更新資料庫並清除 Redis 資料
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        redis_token_manager: RedisTokenManager,
    ):
        self.user_repository = user_repository
        self.redis_token_manager = redis_token_manager

    async def execute(self, user_id: str, request: VerifyEmailChangeRequest) -> dict:
        """
        執行 Email 變更驗證

        Args:
            user_id: 使用者 ID（字串，從 Redis 查詢用）
            request: VerifyEmailChangeRequest DTO（含 token 與 type）

        Returns:
            dict: 驗證狀態，包含 `status` 與 `message`

        Raises:
            ValidationError: Token 無效、已過期，或無待處理的 Email 變更請求
        """
        token_type = request.type.value  # "old" or "new"

        # 1. 驗證 token 正確性
        is_valid = await self.redis_token_manager.verify_token(
            user_id=user_id,
            token=request.token,
            token_type=token_type,
        )
        if not is_valid:
            raise ValidationError("驗證連結無效或已過期")

        # 2. 標記該端已驗證
        await self.redis_token_manager.mark_as_verified(
            user_id=user_id,
            token_type=token_type,
        )

        # 3. 檢查兩端是否都已驗證
        both_verified = await self.redis_token_manager.check_both_verified(user_id)

        if both_verified:
            # 取得待處理的新 Email
            pending_email = await self.redis_token_manager.get_pending_email(user_id)
            if pending_email is None:
                raise ValidationError("找不到待處理的 Email 變更請求")

            # 更新資料庫
            from uuid import UUID
            user = await self.user_repository.get_by_id(UUID(user_id))
            if user is None:
                raise ValidationError("使用者不存在")

            user.email = pending_email  # type: ignore[assignment]
            await self.user_repository.update(user)

            # 清除 Redis 資料
            await self.redis_token_manager.cleanup_email_change(user_id)

            return {
                "status": "completed",
                "message": "Email 已成功更新",
            }

        return {
            "status": "pending",
            "message": f"{'舊' if token_type == 'old' else '新'} Email 已驗證，等待另一端確認",
        }
