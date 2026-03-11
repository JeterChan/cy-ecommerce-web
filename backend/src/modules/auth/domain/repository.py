from abc import ABC, abstractmethod
from typing import Optional, List

from modules.auth.domain.entities import UserEntity

class IUserRepository(ABC):
    """
    User Data 存取介面 (抽象層)

    職責：
    - 定義所有 User 相關資料操作契約
    - 不依賴任何具體技術實作 (ex. SQLAlchemy)
    - 使用 Domain Entity (而非 ORM model)
    """

    @abstractmethod
    async def create(self, user: UserEntity) -> UserEntity:
        """建立新使用者"""
        pass

    @abstractmethod
    async def get_by_id(self, user_id) -> Optional[UserEntity]:
        """根據 ID 查詢 User"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        """根據 Email 查詢 User"""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[UserEntity]:
        """根據使用者名稱查詢使用者"""
        pass

    @abstractmethod
    async def update(self, user: UserEntity) -> UserEntity:
        """更新使用者資料 (可用於啟用、變更密碼、軟刪除)"""
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """檢查 Email 是否已存在"""
        pass

    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """檢查使用者名稱是否已存在"""
        pass
