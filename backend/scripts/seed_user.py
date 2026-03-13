"""
一般用戶種子腳本

建立一個用於手動測試的一般會員帳號（role: user）。
已存在時自動更新密碼與驗證狀態，可安全重複執行。

執行方式：
  cd backend
  python -m scripts.seed_user
"""
import asyncio
import uuid
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from infrastructure.config import settings
from modules.auth.infrastructure.models import UserModel
from modules.auth.infrastructure.password_hasher import BcryptPasswordHasher


async def seed_user():
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    hasher = BcryptPasswordHasher()

    async with async_session() as session:
        result = await session.execute(
            select(UserModel).where(UserModel.email == "user@test.com")
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("測試帳號 user@test.com 已存在，更新密碼與驗證狀態...")
            existing_user.role = "user"
            existing_user.is_verified = True
            existing_user.is_active = True
            existing_user.password_hash = hasher.hash("User123!")
        else:
            print("正在建立測試一般用戶帳號...")
            new_user = UserModel(
                id=uuid.uuid4(),
                email="user@test.com",
                username="test_user",
                password_hash=hasher.hash("User123!"),
                role="user",
                is_verified=True,
                is_active=True,
            )
            session.add(new_user)

        await session.commit()
        print("✅ 測試帳號建立/更新成功！")
        print("   Email:    user@test.com")
        print("   Password: User123!")
        print("   Role:     user")


if __name__ == "__main__":
    asyncio.run(seed_user())
