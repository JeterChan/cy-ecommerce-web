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
        """
        初始化 Brevo 服務

        Args:
            api_key: Brevo API Key
            sender_email: 寄件人電子郵件地址
            sender_name: 寄件人名稱
            frontend_url: 前端 URL（用於生成驗證連結）
        """
        self.api_key = api_key
        self.sender_email = sender_email
        self.sender_name = sender_name
        self.frontend_url = frontend_url or "http://localhost:5173"
        self.api_url = "https://api.brevo.com/v3/smtp/email"

    async def send_email_verification(
        self,
        to_email: str,
        username: str,
        verification_url: str,
        email_type: str
    ) -> None:
        """
        實作：發送電子郵件驗證信

        Args:
            to_email: 收件人電子郵件地址
            username: 使用者名稱
            verification_url: 驗證連結 URL
            email_type: 電子郵件類型 ("old" 或 "new")

        Raises:
            EmailSendError: 當郵件發送失敗時
        """
        # 根據 email_type 選擇不同的郵件模板
        if email_type == "old":
            subject = "驗證您的舊電子郵件地址"
            html_content = self._render_old_email_template(username, verification_url)
        elif email_type == "new":
            subject = "驗證您的新電子郵件地址"
            html_content = self._render_new_email_template(username, verification_url)
        else:
            raise ValueError(f"不支援的 email_type: {email_type}")

        await self._send_via_api(to_email, subject, html_content)

    async def _send_via_api(
        self,
        to_email: str,
        subject: str,
        html_content: str
    ) -> None:
        """
        內部方法：透過 Brevo API 發送郵件

        Args:
            to_email: 收件人電子郵件地址
            subject: 郵件主旨
            html_content: HTML 格式的郵件內容

        Raises:
            EmailSendError: 當 API 呼叫失敗時
        """
        headers = {
            "accept": "application/json",
            "api-key": self.api_key,
            "content-type": "application/json"
        }

        payload = {
            "sender": {
                "name": self.sender_name,
                "email": self.sender_email
            },
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html_content
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                logger.info(f"成功發送郵件至 {to_email}, 主旨: {subject}")

        except httpx.HTTPStatusError as e:
            logger.error(f"Brevo API 回應錯誤: {e.response.status_code} - {e.response.text}")
            raise EmailSendError(f"郵件發送失敗: API 錯誤 {e.response.status_code}") from e

        except httpx.RequestError as e:
            logger.error(f"Brevo API 請求失敗: {str(e)}")
            raise EmailSendError(f"郵件發送失敗: 網路錯誤") from e

        except Exception as e:
            logger.error(f"郵件發送發生未預期錯誤: {str(e)}")
            raise EmailSendError(f"郵件發送失敗: {str(e)}") from e

    def _render_old_email_template(self, username: str, verification_url: str) -> str:
        """
        渲染舊電子郵件驗證模板

        Args:
            username: 使用者名稱
            verification_url: 驗證連結 URL

        Returns:
            HTML 格式的郵件內容
        """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>驗證您的舊電子郵件地址</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f4f4f4; padding: 20px; border-radius: 5px;">
                <h2 style="color: #2c3e50; margin-top: 0;">您好，{username}</h2>
                <p>您正在變更您的電子郵件地址。</p>
                <p>為了確保帳戶安全，我們需要驗證您目前的電子郵件地址。</p>
                <p style="margin: 30px 0;">
                    <a href="{verification_url}" 
                       style="background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        驗證舊電子郵件
                    </a>
                </p>
                <p style="color: #7f8c8d; font-size: 14px;">
                    或複製以下連結到瀏覽器：<br>
                    <span style="word-break: break-all;">{verification_url}</span>
                </p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="color: #e74c3c; font-size: 14px;">
                    ⚠️ 此連結將在 24 小時後失效。
                </p>
                <p style="color: #7f8c8d; font-size: 12px;">
                    如果您沒有進行此操作，請忽略此郵件。
                </p>
            </div>
        </body>
        </html>
        """

    def _render_new_email_template(self, username: str, verification_url: str) -> str:
        """
        渲染新電子郵件驗證模板

        Args:
            username: 使用者名稱
            verification_url: 驗證連結 URL

        Returns:
            HTML 格式的郵件內容
        """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>驗證您的新電子郵件地址</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f4f4f4; padding: 20px; border-radius: 5px;">
                <h2 style="color: #27ae60; margin-top: 0;">歡迎，{username}</h2>
                <p>您正在將帳戶的電子郵件地址變更為此信箱。</p>
                <p>請點擊下方按鈕驗證您的新電子郵件地址，以完成變更。</p>
                <p style="margin: 30px 0;">
                    <a href="{verification_url}" 
                       style="background-color: #27ae60; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        驗證新電子郵件
                    </a>
                </p>
                <p style="color: #7f8c8d; font-size: 14px;">
                    或複製以下連結到瀏覽器：<br>
                    <span style="word-break: break-all;">{verification_url}</span>
                </p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="color: #e74c3c; font-size: 14px;">
                    ⚠️ 此連結將在 24 小時後失效。
                </p>
                <p style="color: #7f8c8d; font-size: 12px;">
                    如果您沒有進行此操作，請立即聯絡客服。
                </p>
            </div>
        </body>
        </html>
        """

