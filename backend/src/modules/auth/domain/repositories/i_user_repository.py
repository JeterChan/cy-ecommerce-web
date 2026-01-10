from abc import ABC, abstractmethod
from typing import Optional, List

from src.modules.auth.domain.entities import UserEntity

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
            user (UserEntity): User entity to persist.
        
        Returns:
            UserEntity: The created user entity including generated fields such as `id`.
        """
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        """
        Retrieve a user by their numeric ID.
        
        Parameters:
            user_id (int): The user's numeric identifier.
        
        Returns:
            UserEntity or `None`: `UserEntity` if a user with the given ID exists, `None` otherwise.
        """
        pass

    @abstractmethod
    async def get_by_email(self, email:str) -> Optional[UserEntity]:
        """
        Retrieve a user by email.
        
        Returns:
            UserEntity if a user with the given email exists, `None` otherwise.
        """
        pass

    @abstractmethod
    async def get_by_username(self, username:str) -> Optional[UserEntity]:
        """
        Retrieve a user by username.
        
        Parameters:
            username (str): The username to look up.
        
        Returns:
            Optional[UserEntity]: `UserEntity` if a user with the given username exists, `None` otherwise.
        """
        pass

    @abstractmethod
    async def get_all(self, skip: int=0, limit: int=100) -> List[UserEntity]:
        """
        Retrieve a paginated list of users.
        
        Parameters:
            skip (int): Number of records to skip before collecting results.
            limit (int): Maximum number of records to return.
        
        Returns:
            List[UserEntity]: List of users according to the pagination parameters; empty list if no users are found.
        """
        pass

    @abstractmethod
    async def update(self, user_id:int, user_data:dict) -> UserEntity:
        """
        Update a user's fields and return the updated UserEntity.
        
        Parameters:
            user_id (int): ID of the user to update.
            user_data (dict): Mapping of fields to update and their new values.
        
        Returns:
            UserEntity: The updated user entity with applied changes.
        
        Raises:
            UserNotFoundError: If no user exists with the given `user_id`.
        """
        pass

    @abstractmethod
    async def delete(self, user_id:int) -> bool:
        """
        Remove the user with the given ID.
        
        Parameters:
            user_id (int): ID of the user to remove.
        
        Returns:
            bool: `True` if the user was deleted, `False` otherwise.
        """
        pass

    @abstractmethod
    async def exists_by_email(self, email:str) -> bool:
        """
        Determine whether a user with the given email exists.
        
        Returns:
            `true` if a user with the given email exists, `false` otherwise.
        """
        pass