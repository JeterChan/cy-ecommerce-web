from abc import ABC, abstractmethod
from typing import Optional, List

from pydantic import UUID4
from modules.auth.domain.entity import UserEntity

class IUserRepository(ABC):
    """
    User Data 存取介面 (抽象層)

    職責：
    - 定義所有 User 相關資料操作契約
    - 不依賴任何具體技術實作 (ex. SQLAlchemy)
    - 使用 Domain Entity (而非 ORM model)

    使用場景：
    - Use Case Layer 依賴此介面
    - Infrastructure Layer 實作此介面
    """

    @abstractmethod
    async def create(self, user: UserEntity) -> UserEntity:
        """
        Create a new user in the repository.
        
        Parameters:
            user (UserEntity): User entity to persist; may omit storage-generated fields (e.g., id).
        
        Returns:
            UserEntity: Persisted user entity including storage-generated fields (such as `id`).
        """
        pass

    # @abstractmethod
    # async def get_by_id(self, user_id: int) -> Optional[UserEntity]:
    #     """
    #     根據 ID 查詢 User
    #     :param user_id: 使用者 ID
    #     :return: User Entity or None
    #     """
    #     pass

    @abstractmethod
    async def get_by_email(self, email:str) -> Optional[UserEntity]:
        """
        Retrieve a user by email.
        
        Parameters:
            email (str): The user's email address to look up.
        
        Returns:
            Optional[UserEntity]: UserEntity if a user with the given email exists, None otherwise.
        """
        pass

    # @abstractmethod
    # async def get_by_username(self, username:str) -> Optional[UserEntity]:
    #     """
    #            根據使用者名稱查詢使用者
    #
    #            Args:
    #                username: 使用者名稱
    #
    #            Returns:
    #                User Entity 或 None
    #            """
    #     pass
    #
    # @abstractmethod
    # async def get_all(self, skip: int=0, limit: int=100) -> List[UserEntity]:
    #     """
    #     查詢所有使用者(分頁）
    #     :param skip: 跳過的紀錄數
    #     :param limit: 返回最大的紀錄數
    #     :return: User Entity 列表
    #     """
    #     pass
    #
    # @abstractmethod
    # async def update(self, user_id:int, user_data:dict) -> UserEntity:
    #     """
    #     update user data
    #     :param user_id: user id
    #     :param user_data: 要更新的欄位字典
    #     :return: 更新後的 User Entity
    #     Raises:
    #         UserNotFoundError: 當使用者不存在時拋出
    #     """
    #     pass
    #
    # @abstractmethod
    # async def delete(self, user_id:int) -> bool:
    #     """
    #     刪除使用者
    #     :param user_id: user id
    #     :return: True or False
    #     """
    #     pass

    @abstractmethod
    async def exists_by_email(self, email:str) -> bool:
        """
        Determine whether a user with the given email exists in the repository.
        
        Returns:
            True if a user with the email exists, False otherwise.
        """
        pass