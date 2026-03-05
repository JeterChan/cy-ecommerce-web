from typing import Protocol


class IEmailService(Protocol):
    """電子郵件服務介面（領域層）"""

    async def send_email_verification(
        self,
        to_email: str,
        username: str,
        verification_url: str,
        email_type: str  # "old" 或 "new"
    ) -> None:
        """
        發送電子郵件驗證信

        Args:
            to_email: 收件人電子郵件地址
            username: 使用者名稱
            verification_url: 驗證連結 URL
            email_type: 電子郵件類型 ("old" 表示舊信箱驗證, "new" 表示新信箱驗證)

        Raises:
            EmailSendError: 當郵件發送失敗時
        """
        ...

