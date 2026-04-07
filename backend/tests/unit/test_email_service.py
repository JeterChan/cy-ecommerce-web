"""
Unit Tests for Email Service

測試範圍：
- 測試 BrevoEmailService 的郵件發送功能
- 測試郵件模板渲染
- 測試錯誤處理
"""

import pytest
from unittest.mock import patch, MagicMock
import httpx

from infrastructure.email.brevo_service import BrevoEmailService, EmailSendError

# 使用 anyio 作為 async backend
pytestmark = pytest.mark.anyio


class TestBrevoEmailService:
    """測試 Brevo Email Service"""

    @pytest.fixture
    def email_service(self):
        """建立 BrevoEmailService 實例"""
        return BrevoEmailService(
            api_key="test_api_key",
            sender_email="noreply@example.com",
            sender_name="測試平台",
            frontend_url="http://localhost:5173",
        )

    def test_initialization(self, email_service):
        """測試初始化"""
        assert email_service.api_key == "test_api_key"
        assert email_service.sender_email == "noreply@example.com"
        assert email_service.sender_name == "測試平台"
        assert email_service.frontend_url == "http://localhost:5173"
        assert email_service.api_url == "https://api.brevo.com/v3/smtp/email"

    def test_render_old_email_template(self, email_service):
        """測試舊信箱驗證郵件模板"""
        html = email_service._render_old_email_template(
            username="TestUser",
            verification_url="http://example.com/verify?token=abc123",
        )

        assert "TestUser" in html
        assert "http://example.com/verify?token=abc123" in html
        assert "驗證舊電子郵件" in html
        assert "24 小時後失效" in html

    def test_render_new_email_template(self, email_service):
        """測試新信箱驗證郵件模板"""
        html = email_service._render_new_email_template(
            username="TestUser",
            verification_url="http://example.com/verify?token=xyz789",
        )

        assert "TestUser" in html
        assert "http://example.com/verify?token=xyz789" in html
        assert "驗證新電子郵件" in html
        assert "24 小時後失效" in html

    async def test_send_email_verification_old_type(self, email_service):
        """測試發送舊信箱驗證郵件"""
        with patch("httpx.AsyncClient.post") as mock_post:
            # Mock 成功回應
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            await email_service.send_email_verification(
                to_email="user@old.com",
                username="TestUser",
                verification_url="http://example.com/verify?token=abc123",
                email_type="old",
            )

            # 驗證 API 被呼叫
            mock_post.assert_called_once()
            call_kwargs = mock_post.call_args.kwargs

            assert call_kwargs["json"]["to"][0]["email"] == "user@old.com"
            assert call_kwargs["json"]["subject"] == "驗證您的舊電子郵件地址"
            assert "TestUser" in call_kwargs["json"]["htmlContent"]

    async def test_send_email_verification_new_type(self, email_service):
        """測試發送新信箱驗證郵件"""
        with patch("httpx.AsyncClient.post") as mock_post:
            # Mock 成功回應
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            await email_service.send_email_verification(
                to_email="user@new.com",
                username="TestUser",
                verification_url="http://example.com/verify?token=xyz789",
                email_type="new",
            )

            # 驗證 API 被呼叫
            mock_post.assert_called_once()
            call_kwargs = mock_post.call_args.kwargs

            assert call_kwargs["json"]["to"][0]["email"] == "user@new.com"
            assert call_kwargs["json"]["subject"] == "驗證您的新電子郵件地址"

    async def test_send_email_verification_invalid_type(self, email_service):
        """測試不支援的 email_type"""
        with pytest.raises(ValueError, match="不支援的 email_type"):
            await email_service.send_email_verification(
                to_email="user@example.com",
                username="TestUser",
                verification_url="http://example.com/verify",
                email_type="invalid",
            )

    async def test_send_via_api_success(self, email_service):
        """測試 API 呼叫成功"""
        with patch("httpx.AsyncClient.post") as mock_post:
            # Mock 成功回應
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            await email_service._send_via_api(
                to_email="test@example.com",
                subject="測試主旨",
                html_content="<p>測試內容</p>",
            )

            # 驗證呼叫參數
            call_kwargs = mock_post.call_args.kwargs
            assert call_kwargs["json"]["sender"]["email"] == "noreply@example.com"
            assert call_kwargs["json"]["sender"]["name"] == "測試平台"
            assert call_kwargs["json"]["to"][0]["email"] == "test@example.com"
            assert call_kwargs["json"]["subject"] == "測試主旨"
            assert call_kwargs["json"]["htmlContent"] == "<p>測試內容</p>"
            assert call_kwargs["headers"]["api-key"] == "test_api_key"

    async def test_send_via_api_http_error(self, email_service):
        """測試 API 回應錯誤"""
        with patch("httpx.AsyncClient.post") as mock_post:
            # Mock HTTP 錯誤
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.text = "Bad Request"
            mock_post.return_value = mock_response
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Bad Request", request=MagicMock(), response=mock_response
            )

            with pytest.raises(EmailSendError, match="API 錯誤 400"):
                await email_service._send_via_api(
                    to_email="test@example.com",
                    subject="測試",
                    html_content="<p>測試</p>",
                )

    async def test_send_via_api_network_error(self, email_service):
        """測試網路錯誤"""
        with patch("httpx.AsyncClient.post") as mock_post:
            # Mock 網路錯誤
            mock_post.side_effect = httpx.RequestError("Connection failed")

            with pytest.raises(EmailSendError, match="網路錯誤"):
                await email_service._send_via_api(
                    to_email="test@example.com",
                    subject="測試",
                    html_content="<p>測試</p>",
                )

    async def test_send_via_api_unexpected_error(self, email_service):
        """測試未預期錯誤"""
        with patch("httpx.AsyncClient.post") as mock_post:
            # Mock 未預期錯誤
            mock_post.side_effect = Exception("Unexpected error")

            with pytest.raises(EmailSendError, match="郵件發送失敗"):
                await email_service._send_via_api(
                    to_email="test@example.com",
                    subject="測試",
                    html_content="<p>測試</p>",
                )
