"""
Email 非同步 Celery 任務

負責非同步發送電子郵件（如 Email 變更驗證信、註冊驗證、密碼重設）。
"""
import asyncio
import logging

from infrastructure.celery_app import celery_app
from infrastructure.config import settings

logger = logging.getLogger(__name__)

def get_email_service():
    from infrastructure.email.brevo_service import BrevoEmailService
    return BrevoEmailService(
        api_key=settings.BREVO_API_KEY,
        sender_email=settings.BREVO_SENDER_EMAIL,
        sender_name=settings.BREVO_SENDER_NAME,
        frontend_url=settings.FRONTEND_URL,
    )

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
    email_service = get_email_service()
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

@celery_app.task(
    name="infrastructure.tasks.email_tasks.send_registration_verification",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_registration_verification(
    self,
    to_email: str,
    username: str,
    verification_url: str,
) -> None:
    """發送註冊驗證信"""
    email_service = get_email_service()
    try:
        asyncio.run(
            email_service.send_registration_verification(
                to_email=to_email,
                username=username,
                verification_url=verification_url,
            )
        )
        logger.info("✅ 註冊驗證信已發送至 %s", to_email)
    except Exception as exc:
        logger.error("❌ 註冊驗證信發送失敗 (%s): %s", to_email, exc)
        raise self.retry(exc=exc)

@celery_app.task(
    name="infrastructure.tasks.email_tasks.send_password_reset",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_password_reset(
    self,
    to_email: str,
    username: str,
    reset_url: str,
) -> None:
    """發送密碼重設信"""
    email_service = get_email_service()
    try:
        asyncio.run(
            email_service.send_password_reset(
                to_email=to_email,
                username=username,
                reset_url=reset_url,
            )
        )
        logger.info("✅ 密碼重設信已發送至 %s", to_email)
    except Exception as exc:
        logger.error("❌ 密碼重設信發送失敗 (%s): %s", to_email, exc)
        raise self.retry(exc=exc)
