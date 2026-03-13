import httpx
import logging


logger = logging.getLogger(__name__)


class EmailSendError(Exception):
    """郵件發送失敗例外"""
    pass


class BrevoEmailService:
    """Brevo 電子郵件服務實作（基礎設施層）"""

    def __init__(
        self,
        api_key: str,
        sender_email: str,
        sender_name: str,
        frontend_url: str | None = None
    ):
        self.api_key = api_key
        self.sender_email = sender_email
        self.sender_name = sender_name
        self.frontend_url = frontend_url or "http://localhost:5173"
        self.api_url = "https://api.brevo.com/v3/smtp/email"

    async def send_email_verification(self, to_email: str, username: str, verification_url: str, email_type: str) -> None:
        """發送電子郵件變更驗證信 (Existing)"""
        if email_type == "old":
            subject = "驗證您的舊電子郵件地址"
            html_content = self._render_old_email_template(username, verification_url)
        elif email_type == "new":
            subject = "驗證您的新電子郵件地址"
            html_content = self._render_new_email_template(username, verification_url)
        else:
            raise ValueError(f"不支援的 email_type: {email_type}")
        await self._send_via_api(to_email, subject, html_content)

    async def send_registration_verification(self, to_email: str, username: str, verification_url: str) -> None:
        """發送註冊信箱驗證信"""
        subject = "歡迎註冊！請驗證您的電子郵件地址"
        html_content = self._render_registration_template(username, verification_url)
        await self._send_via_api(to_email, subject, html_content)

    async def send_password_reset(self, to_email: str, username: str, reset_url: str) -> None:
        """發送密碼重設信"""
        subject = "重設您的密碼"
        html_content = self._render_password_reset_template(username, reset_url)
        await self._send_via_api(to_email, subject, html_content)

    async def _send_via_api(self, to_email: str, subject: str, html_content: str) -> None:
        headers = {
            "accept": "application/json",
            "api-key": self.api_key,
            "content-type": "application/json"
        }
        payload = {
            "sender": {"name": self.sender_name, "email": self.sender_email},
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html_content
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.api_url, json=payload, headers=headers)
                response.raise_for_status()
                logger.info(f"成功發送郵件至 {to_email}, 主旨: {subject}")
        except Exception as e:
            logger.error(f"郵件發送失敗: {str(e)}")
            raise EmailSendError(f"郵件發送失敗: {str(e)}") from e

    def _render_registration_template(self, username: str, verification_url: str) -> str:
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>驗證您的信箱</title></head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f4f4f4; padding: 20px; border-radius: 5px;">
                <h2 style="color: #2c3e50;">您好，{username}</h2>
                <p>感謝您註冊我們的服務！請點擊下方按鈕驗證您的信箱以啟用帳號：</p>
                <p style="margin: 30px 0;">
                    <a href="{verification_url}" style="background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">驗證電子郵件</a>
                </p>
                <p style="color: #e74c3c; font-size: 14px;">⚠️ 此連結將在 24 小時後失效。</p>
            </div>
        </body>
        </html>
        """

    def _render_password_reset_template(self, username: str, reset_url: str) -> str:
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>重設您的密碼</title></head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f4f4f4; padding: 20px; border-radius: 5px;">
                <h2 style="color: #2c3e50;">您好，{username}</h2>
                <p>我們收到了您的密碼重設請求。請點擊下方按鈕重設您的密碼：</p>
                <p style="margin: 30px 0;">
                    <a href="{reset_url}" style="background-color: #e67e22; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">重設密碼</a>
                </p>
                <p style="color: #e74c3c; font-size: 14px;">⚠️ 此連結將在 1 小時後失效。如果您沒有進行此操作，請忽略此郵件。</p>
            </div>
        </body>
        </html>
        """

    def _render_old_email_template(self, username: str, verification_url: str) -> str:
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>驗證您的舊電子郵件地址</title></head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f4f4f4; padding: 20px; border-radius: 5px;">
                <h2 style="color: #2c3e50;">您好，{username}</h2>
                <p>正在驗證您目前的電子郵件地址：</p>
                <p style="margin: 30px 0;">
                    <a href="{verification_url}" style="background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">驗證舊電子郵件</a>
                </p>
                <p style="color: #e74c3c; font-size: 14px;">⚠️ 此連結將在 24 小時後失效。</p>
            </div>
        </body>
        </html>
        """

    def _render_new_email_template(self, username: str, verification_url: str) -> str:
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>驗證您的新電子郵件地址</title></head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f4f4f4; padding: 20px; border-radius: 5px;">
                <h2 style="color: #27ae60;">您好，{username}</h2>
                <p>請點擊下方按鈕驗證您的新電子郵件地址：</p>
                <p style="margin: 30px 0;">
                    <a href="{verification_url}" style="background-color: #27ae60; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">驗證新電子郵件</a>
                </p>
                <p style="color: #e74c3c; font-size: 14px;">⚠️ 此連結將在 24 小時後失效。</p>
            </div>
        </body>
        </html>
        """
