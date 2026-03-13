import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# 修正匯入路徑，確保能抓到 backend/src 下的模組
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from infrastructure.config import settings
from modules.auth.infrastructure.models import UserModel
from modules.auth.infrastructure.password_hasher import BcryptPasswordHasher

async def seed_admin():
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    hasher = BcryptPasswordHasher()

    async with async_session() as session:
        # 檢查是否已存在
        result = await session.execute(select(UserModel).where(UserModel.email == "admin@test.com"))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("測試帳號 admin@test.com 已存在，更新權限與驗證狀態...")
            existing_user.role = "admin"
            existing_user.is_verified = True
            existing_user.is_active = True
            # 更新密碼為 Admin123!
            existing_user.password_hash = hasher.hash("Admin123!")
        else:
            print("正在建立測試管理員帳號...")
            new_admin = UserModel(
                id=uuid.uuid4(),
                email="admin@test.com",
                username="test_admin",
                password_hash=hasher.hash("Admin123!"),
                role="admin",
                is_verified=True,
                is_active=True
            )
            session.add(new_admin)
        
        await session.commit()
        print("✅ 測試帳號建立/更新成功！")
        print("   Email: admin@test.com")
        print("   Password: Admin123!")

if __name__ == "__main__":
    asyncio.run(seed_admin())
