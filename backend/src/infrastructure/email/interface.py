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
        """發送電子郵件變更驗證信 (Existing)"""
        ...

    async def send_registration_verification(
        self,
        to_email: str,
        username: str,
        verification_url: str
    ) -> None:
        """發送註冊信箱驗證信"""
        ...

    async def send_password_reset(
        self,
        to_email: str,
        username: str,
        reset_url: str
    ) -> None:
        """發送密碼重設信"""
        ...
