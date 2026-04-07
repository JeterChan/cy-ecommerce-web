"""
Email 寄送服務整合測試

測試範圍（三層完整覆蓋）：
  1. BrevoEmailService   — 驗證傳給 Brevo API 的 payload 結構與錯誤處理（mock httpx）
  2. Celery Email Task  — 驗證任務同步執行與 retry 機制（sync context, mock Brevo）
  3. Email Change API   — 完整 HTTP 流程：FastAPI → Real Redis → Real PostgreSQL → Mock Brevo

執行環境：
  - PostgreSQL 服務需正在運行（TEST_DB_* 環境變數 / .env.test）
  - Redis 服務需正在運行於 localhost:6379（使用 DB 15 作為測試隔離庫）
  - Brevo HTTP 呼叫以 unittest.mock.patch 取代，不發送真實郵件

執行方式：
    cd backend
    pytest tests/integration/test_email_change_flow.py -v
"""

import os
import pytest
import pytest_asyncio
import httpx
from unittest.mock import MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from redis.asyncio import Redis

from infrastructure.database import Base
from infrastructure.redis.token_manager import RedisTokenManager
from infrastructure.email.brevo_service import BrevoEmailService, EmailSendError
from modules.auth.infrastructure.repositories.user_repository import UserRepository
from modules.auth.domain.entities.UserEntity import UserEntity
from core.security import get_password_hash, create_access_token

# ──────────────────────────────────────────────
# 測試資料庫設定
# ──────────────────────────────────────────────

TEST_DATABASE_URL = (
    "postgresql+asyncpg://"
    f"{os.getenv('TEST_DB_USER', 'user')}:{os.getenv('TEST_DB_PASSWORD', 'password')}"
    f"@{os.getenv('TEST_DB_HOST', 'localhost')}:{os.getenv('TEST_DB_PORT', '5432')}"
    f"/{os.getenv('TEST_DB_NAME', 'test_ecommerce_db')}"
)

REDIS_TEST_DB = 15  # 獨立測試 DB，與開發環境隔離


# ──────────────────────────────────────────────
# 共用 Fixtures
# ──────────────────────────────────────────────


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """每個測試函式前後 drop/create 全部資料表，確保測試隔離。"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine) -> AsyncSession:
    """提供測試用 AsyncSession，測試後 rollback 未提交的殘餘變更。"""
    factory = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def redis_client() -> Redis:
    """連接 Redis DB 15，測試前後清空，確保測試隔離。"""
    client = await Redis.from_url(
        f"redis://localhost:6379/{REDIS_TEST_DB}",
        encoding="utf-8",
        decode_responses=True,
    )
    await client.flushdb()
    yield client
    await client.flushdb()
    await client.aclose()


@pytest_asyncio.fixture
async def user_repository(async_session) -> UserRepository:
    return UserRepository(async_session)


@pytest_asyncio.fixture
async def existing_user(user_repository) -> UserEntity:
    """在測試 DB 中建立並 commit 標準測試使用者。"""
    user = UserEntity(
        username="email_change_tester",
        email="old_email@example.com",
        password_hash=get_password_hash("SecurePass123!"),
        is_active=True,
    )
    return await user_repository.create(user)


@pytest.fixture
def mock_brevo_ok():
    """回傳模擬 Brevo API 成功（HTTP 201）的 patch context。"""
    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.raise_for_status = MagicMock()
    with patch("httpx.AsyncClient.post", return_value=mock_resp) as mock_post:
        yield mock_post


# ══════════════════════════════════════════════════════════════════
# 1. BrevoEmailService 整合測試
# ══════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
class TestBrevoEmailServiceIntegration:
    """
    直接呼叫 BrevoEmailService，以 mock httpx 取代真實 HTTP 呼叫。
    驗證傳給 Brevo API 的 payload 結構、headers 及錯誤處理行為。
    """

    @pytest.fixture
    def email_service(self):
        return BrevoEmailService(
            api_key="test-brevo-api-key",
            sender_email="noreply@cy-ecommerce.com",
            sender_name="CyWeb 測試",
            frontend_url="http://localhost:5173",
        )

    async def test_old_email_payload_structure(self, email_service, mock_brevo_ok):
        """舊信箱驗證信：驗證傳給 Brevo 的 payload 各欄位正確。"""
        await email_service.send_email_verification(
            to_email="old@example.com",
            username="測試用戶",
            verification_url="http://localhost:5173/email/verify?token=abc123&type=old",
            email_type="old",
        )

        assert mock_brevo_ok.called
        payload = mock_brevo_ok.call_args.kwargs["json"]

        assert payload["to"][0]["email"] == "old@example.com"
        assert payload["subject"] == "驗證您的舊電子郵件地址"
        assert payload["sender"]["email"] == "noreply@cy-ecommerce.com"
        assert payload["sender"]["name"] == "CyWeb 測試"
        assert "測試用戶" in payload["htmlContent"]
        assert "abc123" in payload["htmlContent"]

    async def test_new_email_payload_structure(self, email_service, mock_brevo_ok):
        """新信箱驗證信：驗證 payload 主旨與內容正確。"""
        await email_service.send_email_verification(
            to_email="new@example.com",
            username="測試用戶",
            verification_url="http://localhost:5173/email/verify?token=xyz789&type=new",
            email_type="new",
        )

        payload = mock_brevo_ok.call_args.kwargs["json"]
        assert payload["to"][0]["email"] == "new@example.com"
        assert payload["subject"] == "驗證您的新電子郵件地址"
        assert "xyz789" in payload["htmlContent"]

    async def test_api_key_sent_in_header(self, email_service, mock_brevo_ok):
        """驗證 Brevo API Key 與 content-type 正確放入 request headers。"""
        await email_service.send_email_verification(
            to_email="test@example.com",
            username="user",
            verification_url="http://localhost:5173/verify",
            email_type="old",
        )

        headers = mock_brevo_ok.call_args.kwargs["headers"]
        assert headers["api-key"] == "test-brevo-api-key"
        assert headers["accept"] == "application/json"
        assert headers["content-type"] == "application/json"

    async def test_brevo_api_url_is_correct(self, email_service, mock_brevo_ok):
        """驗證請求送往正確的 Brevo API endpoint。"""
        await email_service.send_email_verification(
            to_email="test@example.com",
            username="user",
            verification_url="http://localhost:5173/verify",
            email_type="new",
        )

        call_url = mock_brevo_ok.call_args.args[0]
        assert "brevo.com" in call_url
        assert "smtp/email" in call_url

    async def test_http_401_raises_email_send_error(self, email_service):
        """Brevo API 回傳 401 時應拋出 EmailSendError，帶有 API 錯誤碼資訊。"""
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Unauthorized", request=MagicMock(), response=mock_resp
        )

        with patch("httpx.AsyncClient.post", return_value=mock_resp):
            with pytest.raises(EmailSendError, match="API 錯誤 401"):
                await email_service.send_email_verification(
                    to_email="test@example.com",
                    username="user",
                    verification_url="http://localhost:5173/verify",
                    email_type="old",
                )

    async def test_network_error_raises_email_send_error(self, email_service):
        """網路連線失敗時應拋出 EmailSendError，帶有「網路錯誤」標識。"""
        with patch(
            "httpx.AsyncClient.post",
            side_effect=httpx.RequestError("Connection refused"),
        ):
            with pytest.raises(EmailSendError, match="網路錯誤"):
                await email_service.send_email_verification(
                    to_email="test@example.com",
                    username="user",
                    verification_url="http://localhost:5173/verify",
                    email_type="old",
                )

    async def test_sends_two_separate_emails_for_old_and_new(
        self, email_service, mock_brevo_ok
    ):
        """一次完整流程分別對舊、新信箱發送驗證信，共應觸發 2 次 API 呼叫。"""
        await email_service.send_email_verification(
            to_email="old@example.com",
            username="user",
            verification_url="http://localhost:5173/verify?token=t1&type=old",
            email_type="old",
        )
        await email_service.send_email_verification(
            to_email="new@example.com",
            username="user",
            verification_url="http://localhost:5173/verify?token=t2&type=new",
            email_type="new",
        )

        assert mock_brevo_ok.call_count == 2
        recipients = [
            mock_brevo_ok.call_args_list[0].kwargs["json"]["to"][0]["email"],
            mock_brevo_ok.call_args_list[1].kwargs["json"]["to"][0]["email"],
        ]
        assert "old@example.com" in recipients
        assert "new@example.com" in recipients


# ══════════════════════════════════════════════════════════════════
# 2. Celery Email Task 整合測試（同步 context）
# ══════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestCeleryEmailTaskIntegration:
    """
    使用 Celery task.apply() 在同步 context 中執行任務（無需 broker）。
    mock httpx 取代 Brevo HTTP 呼叫，驗證完整的 Celery → BrevoEmailService 呼叫鏈。

    注意：此 class 為同步測試（非 async），因任務內部使用 asyncio.run()，
    在無事件迴圈的同步環境中可正確執行。
    """

    @pytest.fixture(autouse=True)
    def celery_propagate_errors(self):
        """讓 Celery eager 模式下的任務例外可向上傳遞，便於測試 retry 行為。"""
        from infrastructure.celery_app import celery_app

        original = celery_app.conf.task_eager_propagates
        celery_app.conf.task_eager_propagates = True
        yield
        celery_app.conf.task_eager_propagates = original

    def _make_success_mock(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.raise_for_status = MagicMock()
        return mock_resp

    def test_task_sends_old_email_successfully(self):
        """Celery 任務成功執行：驗證 BrevoEmailService 以正確參數呼叫 Brevo。"""
        from infrastructure.tasks.email_tasks import send_email_change_verification

        with patch(
            "httpx.AsyncClient.post", return_value=self._make_success_mock()
        ) as mock_post:
            result = send_email_change_verification.apply(
                args=[
                    "recipient@example.com",
                    "TestUser",
                    "http://localhost:5173/verify?token=abc&type=old",
                    "old",
                ]
            )

        assert result.successful()
        assert mock_post.called

        payload = mock_post.call_args.kwargs["json"]
        assert payload["to"][0]["email"] == "recipient@example.com"
        assert payload["subject"] == "驗證您的舊電子郵件地址"
        assert "TestUser" in payload["htmlContent"]

    def test_task_sends_new_email_successfully(self):
        """Celery 任務：email_type='new' 時發送新信箱驗證主旨。"""
        from infrastructure.tasks.email_tasks import send_email_change_verification

        with patch(
            "httpx.AsyncClient.post", return_value=self._make_success_mock()
        ) as mock_post:
            result = send_email_change_verification.apply(
                args=[
                    "new@example.com",
                    "TestUser",
                    "http://localhost:5173/verify?token=xyz&type=new",
                    "new",
                ]
            )

        assert result.successful()
        payload = mock_post.call_args.kwargs["json"]
        assert payload["subject"] == "驗證您的新電子郵件地址"
        assert payload["to"][0]["email"] == "new@example.com"

    def test_task_retries_when_brevo_returns_500(self):
        """Brevo API 回傳 5xx 時，任務應觸發 retry 機制（拋出例外）。"""
        from infrastructure.tasks.email_tasks import send_email_change_verification

        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=MagicMock(), response=mock_resp
        )

        with patch("httpx.AsyncClient.post", return_value=mock_resp):
            with pytest.raises(Exception):
                # task_eager_propagates=True → Retry exception 向上傳遞
                send_email_change_verification.apply(
                    args=["fail@example.com", "User", "http://test/url", "old"]
                )

    def test_task_passes_correct_payload_to_brevo(self):
        """驗證任務將正確的 sender 資訊（來自 settings）傳遞給 Brevo。"""
        from infrastructure.tasks.email_tasks import send_email_change_verification
        from infrastructure.config import settings

        with patch(
            "httpx.AsyncClient.post", return_value=self._make_success_mock()
        ) as mock_post:
            send_email_change_verification.apply(
                args=[
                    "test@example.com",
                    "TestUser",
                    "http://localhost:5173/verify",
                    "old",
                ]
            )

        payload = mock_post.call_args.kwargs["json"]
        # Sender 資訊應來自 settings（BREVO_SENDER_EMAIL / BREVO_SENDER_NAME）
        assert payload["sender"]["email"] == settings.BREVO_SENDER_EMAIL
        assert payload["sender"]["name"] == settings.BREVO_SENDER_NAME


# ══════════════════════════════════════════════════════════════════
# 3. Email Change 完整 API 流程整合測試
# ══════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
class TestEmailChangeAPIFlow:
    """
    透過 FastAPI ASGITransport 發送真實 HTTP 請求，串接：
      - Real PostgreSQL（使用 override_get_db 注入測試 session）
      - Real Redis DB 15（使用 override_get_redis 注入測試連線）
      - Mock Celery .delay()（驗證任務被正確 dispatch，不需真實 worker）
      - Mock Brevo httpx（避免發送真實郵件）

    測試涵蓋：
      ✅ 成功申請 Email 變更 → Redis 儲存 token
      ✅ 驗證舊信箱 → pending 狀態
      ✅ 驗證新信箱 → completed + DB email 更新 + Redis 清除
      ✅ 完整端對端流程（3 個 HTTP 請求串接）
      ✅ 密碼錯誤 → 401
      ✅ Email 已被使用 → 409
      ✅ 無效 token → 400
    """

    # ── 共用 helper：建立 FastAPI app 的 dependency overrides ──

    @staticmethod
    def _build_overrides(async_session, redis_client):
        from main import app
        from infrastructure.database import get_db, get_redis

        async def override_get_db():
            yield async_session

        async def override_get_redis():
            yield redis_client

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_redis] = override_get_redis
        return app

    @staticmethod
    def _clear_overrides():
        from main import app

        app.dependency_overrides.clear()

    # ── 測試案例 ──

    async def test_request_email_change_returns_202_and_stores_redis_tokens(
        self,
        async_session: AsyncSession,
        redis_client: Redis,
        existing_user: UserEntity,
    ):
        """
        POST /me/email/change 成功時：
        - 回傳 HTTP 202
        - Redis 中寫入 5 個 email_change:{user_id}:* keys
        - Celery .delay() 被觸發兩次（舊信箱、新信箱各一次）
        - 各次 dispatch 帶有正確的 email_type 與收件人 email
        """
        from httpx import ASGITransport

        app = self._build_overrides(async_session, redis_client)
        access_token = create_access_token({"sub": str(existing_user.email)})
        user_id = str(existing_user.id)

        try:
            with patch(
                "infrastructure.tasks.email_tasks.send_email_change_verification.delay"
            ) as mock_delay:
                async with httpx.AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test"
                ) as client:
                    response = await client.post(
                        "/api/v1/auth/me/email/change",
                        headers={"Authorization": f"Bearer {access_token}"},
                        json={
                            "new_email": "new_email@example.com",
                            "password": "SecurePass123!",
                        },
                    )

            # HTTP 202 及回應訊息
            assert response.status_code == 202
            assert "驗證信已發送" in response.json()["message"]

            # Celery dispatch 次數：舊信箱 + 新信箱 = 2
            assert mock_delay.call_count == 2

            calls_kwargs = [c.kwargs for c in mock_delay.call_args_list]
            dispatched_types = {kw["email_type"] for kw in calls_kwargs}
            assert dispatched_types == {"old", "new"}

            old_dispatch = next(kw for kw in calls_kwargs if kw["email_type"] == "old")
            new_dispatch = next(kw for kw in calls_kwargs if kw["email_type"] == "new")
            assert old_dispatch["to_email"] == str(existing_user.email)
            assert new_dispatch["to_email"] == "new_email@example.com"
            assert "token=" in old_dispatch["verification_url"]
            assert "token=" in new_dispatch["verification_url"]

            # Redis 中應存有 5 個 keys
            keys = await redis_client.keys(f"email_change:{user_id}:*")
            assert len(keys) == 5

        finally:
            self._clear_overrides()

    async def test_verify_old_email_returns_pending_status(
        self,
        async_session: AsyncSession,
        redis_client: Redis,
        existing_user: UserEntity,
    ):
        """
        GET /me/email/verify?type=old 成功時：
        - 回傳 HTTP 200
        - 回傳 status="pending"（新信箱尚未驗證）
        - Redis old_verified 標記為 "true"
        """
        from httpx import ASGITransport

        token_manager = RedisTokenManager(redis_client)
        old_token = token_manager.generate_token()
        new_token = token_manager.generate_token()
        user_id = str(existing_user.id)

        await token_manager.store_email_change_tokens(
            user_id=user_id,
            old_token=old_token,
            new_token=new_token,
            new_email="new_email@example.com",
        )

        app = self._build_overrides(async_session, redis_client)

        try:
            async with httpx.AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(
                    "/api/v1/auth/me/email/verify",
                    params={"token": old_token, "type": "old", "user_id": user_id},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "pending"
            assert "舊 Email 已驗證" in data["message"]

            # Redis old_verified 應已標記為 true
            old_verified = await redis_client.get(
                f"email_change:{user_id}:old_verified"
            )
            assert old_verified == "true"
            # 新信箱尚未驗證
            new_verified = await redis_client.get(
                f"email_change:{user_id}:new_verified"
            )
            assert new_verified == "false"

        finally:
            self._clear_overrides()

    async def test_verify_new_email_completes_change_and_updates_db(
        self,
        async_session: AsyncSession,
        redis_client: Redis,
        existing_user: UserEntity,
    ):
        """
        雙重驗證完成（已先標記 old 驗證）後驗證新信箱時：
        - 回傳 HTTP 200，status="completed"
        - PostgreSQL 中使用者 email 更新為新 email
        - Redis 中所有 email_change keys 被清除
        """
        from httpx import ASGITransport

        token_manager = RedisTokenManager(redis_client)
        old_token = token_manager.generate_token()
        new_token = token_manager.generate_token()
        user_id = str(existing_user.id)
        new_email = "completed@example.com"

        await token_manager.store_email_change_tokens(
            user_id=user_id,
            old_token=old_token,
            new_token=new_token,
            new_email=new_email,
        )
        # 預先標記舊信箱已驗證
        await token_manager.mark_as_verified(user_id, "old")

        app = self._build_overrides(async_session, redis_client)

        try:
            async with httpx.AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(
                    "/api/v1/auth/me/email/verify",
                    params={"token": new_token, "type": "new", "user_id": user_id},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"
            assert "成功更新" in data["message"]

            # PostgreSQL email 已更新（update() 內部已 commit）
            user_repo = UserRepository(async_session)
            updated_user = await user_repo.get_by_id(existing_user.id)
            assert updated_user is not None
            assert str(updated_user.email) == new_email

            # Redis 中 email_change keys 應已全部清除
            keys = await redis_client.keys(f"email_change:{user_id}:*")
            assert len(keys) == 0

        finally:
            self._clear_overrides()

    async def test_complete_email_change_end_to_end(
        self,
        async_session: AsyncSession,
        redis_client: Redis,
        existing_user: UserEntity,
    ):
        """
        完整端對端流程，串接 3 個 HTTP 請求：

        Step 1: POST /me/email/change → HTTP 202
                └─ Redis 中寫入 old_token / new_token
        Step 2: GET  /me/email/verify?type=old → HTTP 200, status=pending
        Step 3: GET  /me/email/verify?type=new → HTTP 200, status=completed
                └─ DB email 更新為新 email
                └─ Redis email_change keys 清空
        """
        from httpx import ASGITransport

        access_token = create_access_token({"sub": str(existing_user.email)})
        user_id = str(existing_user.id)
        new_email = "final_new@example.com"

        app = self._build_overrides(async_session, redis_client)

        try:
            async with httpx.AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:

                # ── Step 1：申請 Email 變更 ──
                with patch(
                    "infrastructure.tasks.email_tasks.send_email_change_verification.delay"
                ) as mock_delay:
                    r1 = await client.post(
                        "/api/v1/auth/me/email/change",
                        headers={"Authorization": f"Bearer {access_token}"},
                        json={"new_email": new_email, "password": "SecurePass123!"},
                    )
                assert r1.status_code == 202
                assert mock_delay.call_count == 2

                # 從 Redis 取出真實 token（由 use case 自動產生）
                old_token = await redis_client.get(f"email_change:{user_id}:old_token")
                new_token = await redis_client.get(f"email_change:{user_id}:new_token")
                assert old_token is not None
                assert new_token is not None

                # ── Step 2：驗證舊信箱 ──
                r2 = await client.get(
                    "/api/v1/auth/me/email/verify",
                    params={"token": old_token, "type": "old", "user_id": user_id},
                )
                assert r2.status_code == 200
                assert r2.json()["status"] == "pending"

                # ── Step 3：驗證新信箱 → 完成變更 ──
                r3 = await client.get(
                    "/api/v1/auth/me/email/verify",
                    params={"token": new_token, "type": "new", "user_id": user_id},
                )
                assert r3.status_code == 200
                assert r3.json()["status"] == "completed"

            # ── 最終狀態驗證 ──
            user_repo = UserRepository(async_session)
            updated_user = await user_repo.get_by_id(existing_user.id)
            assert updated_user is not None
            assert str(updated_user.email) == new_email

            redis_keys = await redis_client.keys(f"email_change:{user_id}:*")
            assert len(redis_keys) == 0

        finally:
            self._clear_overrides()

    async def test_wrong_password_returns_401(
        self,
        async_session: AsyncSession,
        redis_client: Redis,
        existing_user: UserEntity,
    ):
        """密碼錯誤時應回傳 HTTP 401，且 Redis 中不應有任何 token 被寫入。"""
        from httpx import ASGITransport

        app = self._build_overrides(async_session, redis_client)
        access_token = create_access_token({"sub": str(existing_user.email)})
        user_id = str(existing_user.id)

        try:
            async with httpx.AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/v1/auth/me/email/change",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={
                        "new_email": "another@example.com",
                        "password": "WrongPass123!",
                    },
                )

            assert response.status_code == 401

            # Redis 中不應有任何 token 被寫入
            keys = await redis_client.keys(f"email_change:{user_id}:*")
            assert len(keys) == 0

        finally:
            self._clear_overrides()

    async def test_duplicate_email_returns_409(
        self,
        async_session: AsyncSession,
        redis_client: Redis,
        existing_user: UserEntity,
        user_repository: UserRepository,
    ):
        """目標 Email 已被其他使用者佔用時應回傳 HTTP 409。"""
        from httpx import ASGITransport

        # 建立另一個佔用 email 的使用者（create 內部會 commit）
        taken_user = UserEntity(
            username="another_user",
            email="taken@example.com",
            password_hash=get_password_hash("AnotherPass123!"),
            is_active=True,
        )
        await user_repository.create(taken_user)

        app = self._build_overrides(async_session, redis_client)
        access_token = create_access_token({"sub": str(existing_user.email)})

        try:
            async with httpx.AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/v1/auth/me/email/change",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={
                        "new_email": "taken@example.com",
                        "password": "SecurePass123!",
                    },
                )

            assert response.status_code == 409

        finally:
            self._clear_overrides()

    async def test_invalid_token_returns_400(
        self,
        async_session: AsyncSession,
        redis_client: Redis,
        existing_user: UserEntity,
    ):
        """使用不存在於 Redis 的 token 驗證時應回傳 HTTP 400。"""
        from httpx import ASGITransport

        user_id = str(existing_user.id)
        # 故意不在 Redis 中存入任何 token
        app = self._build_overrides(async_session, redis_client)

        try:
            async with httpx.AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(
                    "/api/v1/auth/me/email/verify",
                    params={
                        "token": "invalid_token_that_does_not_exist",
                        "type": "old",
                        "user_id": user_id,
                    },
                )

            assert response.status_code == 400

        finally:
            self._clear_overrides()

    async def test_verify_endpoint_accessible_without_jwt(
        self,
        async_session: AsyncSession,
        redis_client: Redis,
        existing_user: UserEntity,
    ):
        """
        /me/email/verify 端點不需要 JWT（透過 link 訪問），
        有效 token 應正常回應 200（無需 Authorization header）。
        """
        from httpx import ASGITransport

        token_manager = RedisTokenManager(redis_client)
        old_token = token_manager.generate_token()
        new_token = token_manager.generate_token()
        user_id = str(existing_user.id)

        await token_manager.store_email_change_tokens(
            user_id=user_id,
            old_token=old_token,
            new_token=new_token,
            new_email="verify_no_jwt@example.com",
        )

        app = self._build_overrides(async_session, redis_client)

        try:
            async with httpx.AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # 不帶 Authorization header
                response = await client.get(
                    "/api/v1/auth/me/email/verify",
                    params={"token": old_token, "type": "old", "user_id": user_id},
                )

            assert response.status_code == 200

        finally:
            self._clear_overrides()
