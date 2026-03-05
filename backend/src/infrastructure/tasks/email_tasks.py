"""
Email 非同步 Celery 任務

負責非同步發送電子郵件（如 Email 變更驗證信）。
"""
import asyncio
import logging

from infrastructure.celery_app import celery_app
from infrastructure.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(
    name="infrastructure.tasks.email_tasks.send_email_change_verification",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_email_change_verification(
    self,
    to_email: str,
    username: str,
    verification_url: str,
    email_type: str,
) -> None:
    """
    非同步發送 Email 變更驗證信

    Args:
        self: Celery task 實例（由 bind=True 注入）
        to_email: 收件人 Email
        username: 使用者名稱
        verification_url: 驗證連結
        email_type: "old"（舊信箱）或 "new"（新信箱）
    """
    from infrastructure.email.brevo_service import BrevoEmailService

    email_service = BrevoEmailService(
        api_key=settings.BREVO_API_KEY,
        sender_email=settings.BREVO_SENDER_EMAIL,
        sender_name=settings.BREVO_SENDER_NAME,
        frontend_url=settings.FRONTEND_URL,
    )

    try:
        asyncio.run(
            email_service.send_email_verification(
                to_email=to_email,
                username=username,
                verification_url=verification_url,
                email_type=email_type,
            )
        )
        logger.info("✅ Email 變更驗證信已發送至 %s (%s)", to_email, email_type)
    except Exception as exc:
        logger.error("❌ Email 發送失敗 (%s): %s", to_email, exc)
        raise self.retry(exc=exc)
