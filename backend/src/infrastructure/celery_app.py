"""Celery Application 實例"""
from celery import Celery
from infrastructure.config import settings

# Redis broker URL
_redis_password = f":{settings.REDIS_PASSWORD}@" if settings.REDIS_PASSWORD else ""
REDIS_URL = f"redis://{_redis_password}{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"

celery_app = Celery(
    "cy_ecommerce",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "infrastructure.tasks.email_tasks",
        "infrastructure.tasks.cleanup_tasks",
        "modules.cart.infrastructure.tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Taipei",
    enable_utc=True,
    task_queues={
        "default": {"routing_key": "default"},
        "email_queue": {"routing_key": "email_queue"},
        "cart_sync_queue": {"routing_key": "cart_sync_queue"},
    },
    task_default_queue="default",
    # Celery Beat 排程設定
    beat_schedule={
        "hard-delete-expired-accounts": {
            "task": "infrastructure.tasks.cleanup_tasks.hard_delete_expired_accounts",
            "schedule": 86400.0,  # 每 24 小時執行一次
        },
    },
)
