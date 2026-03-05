"""請求變更電子郵件 Use Case"""
from uuid import UUID

from modules.auth.infrastructure.repositories.user_repository import UserRepository
from modules.auth.application.dtos.inputs import EmailChangeRequest
from infrastructure.redis.token_manager import RedisTokenManager
from infrastructure.config import settings
from core.exceptions import UserNotFoundError, InvalidCredentialsError, ValidationError


class RequestEmailChangeUseCase:
    """
    請求變更電子郵件 Use Case

    流程：
    1. 驗證目前密碼
    2. 確認新 Email 未被使用
    3. 產生 old/new tokens 存入 Redis（TTL: 24 小時）
    4. 觸發 Celery 任務非同步寄送驗證信
    """

    def __init__(
        self,
        user_repository: UserRepository,
        redis_token_manager: RedisTokenManager,
    ):
        self.user_repository = user_repository
        self.redis_token_manager = redis_token_manager

    async def execute(self, user_id: UUID, request: EmailChangeRequest) -> None:
        """
        執行請求 Email 變更

        Args:
            user_id: 當前使用者 ID
            request: EmailChangeRequest DTO（含新 email 與目前密碼）

        Raises:
            UserNotFoundError: 使用者不存在
            InvalidCredentialsError: 密碼錯誤
            ValidationError: 新 Email 已被使用
        """
        # 1. 取得使用者
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"使用者不存在 (id: {user_id})")

        # 2. 驗證目前密碼
        if not user.verify_password(str(request.password)):
            raise InvalidCredentialsError()

        new_email = str(request.new_email)

        # 3. 確認新 Email 未被使用
        existing = await self.user_repository.get_by_email(new_email)
        if existing is not None:
            raise ValidationError(f"Email {new_email} 已被使用")

        # 4. 產生驗證 tokens
        old_token = self.redis_token_manager.generate_token()
        new_token = self.redis_token_manager.generate_token()

        await self.redis_token_manager.store_email_change_tokens(
            user_id=str(user_id),
            old_token=old_token,
            new_token=new_token,
            new_email=new_email,
        )

        # 5. 觸發 Celery 任務寄送驗證信（舊信箱）
        from infrastructure.tasks.email_tasks import send_email_change_verification

        old_verify_url = (
            f"{settings.FRONTEND_URL}/email/verify"
            f"?token={old_token}&type=old&user_id={user_id}"
        )
        new_verify_url = (
            f"{settings.FRONTEND_URL}/email/verify"
            f"?token={new_token}&type=new&user_id={user_id}"
        )

        send_email_change_verification.delay(
            to_email=str(user.email),
            username=user.username,
            verification_url=old_verify_url,
            email_type="old",
        )
        send_email_change_verification.delay(
            to_email=new_email,
            username=user.username,
            verification_url=new_verify_url,
            email_type="new",
        )
