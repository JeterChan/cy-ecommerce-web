import asyncio
import os
from dotenv import load_dotenv
from infrastructure.email.brevo_service import BrevoEmailService


async def test_send_email():
    """測試發送驗證郵件"""
    # 載入環境變數
    load_dotenv()

    # 檢查 API Key 是否載入
    api_key = os.getenv("BREVO_API_KEY")
    print(f"API Key 前 10 個字元：{api_key[:10] if api_key else 'None'}")
    print(f"API Key 長度：{len(api_key) if api_key else 0}")

    if not api_key:
        print("❌ 錯誤: BREVO_API_KEY 環境變數未設定！")
        return

    # 初始化服務
    service = BrevoEmailService(
        api_key=api_key,
        sender_email=os.getenv("BREVO_SENDER_EMAIL"),
        sender_name=os.getenv("BREVO_SENDER_NAME"),
        frontend_url=os.getenv("FRONTEND_URL")
    )

    # 測試收件人（改成你的測試信箱）
    test_email = "jeterchan226@gmail.com"
    test_username = "測試使用者"
    test_verification_url = "http://localhost:5173/verify?token=test123456"

    try:
        # 測試舊信箱驗證
        print("正在發送舊信箱驗證郵件...")
        await service.send_email_verification(
            to_email=test_email,
            username=test_username,
            verification_url=test_verification_url,
            email_type="old"
        )
        print("✅ 舊信箱驗證郵件發送成功！")

        # 等待一下避免太快
        await asyncio.sleep(2)

        # 測試新信箱驗證
        print("正在發送新信箱驗證郵件...")
        await service.send_email_verification(
            to_email=test_email,
            username=test_username,
            verification_url=test_verification_url,
            email_type="new"
        )
        print("✅ 新信箱驗證郵件發送成功！")

    except Exception as e:
        print(f"❌ 發送失敗: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_send_email())
