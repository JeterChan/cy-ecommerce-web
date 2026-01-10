from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional, List
from sqlalchemy.exc import IntegrityError

from src.modules.auth.domain.repositories.i_user_repository import IUserRepository
from src.modules.auth.domain.entities import UserEntity
from src.modules.auth.infrastructure.models.user import UserModel
from src.core.exceptions import DuplicateEmailError, UserNotFoundError

class UserRepository(IUserRepository):
    """
    使用者資料存取層實作 (SQLAlchemy)

    職責：
    - 實作 IUserRepository Interface
    - 處理 Domain Entity 與 ORM Model 的轉換
    - 管理 SQLAlchemy Session
    - 處理資料庫異常
    """

    def __init__(self, session: AsyncSession):
        """
        Store the provided asynchronous SQLAlchemy session for use by repository methods.
        
        Parameters:
            session (AsyncSession): Asynchronous SQLAlchemy session used for database operations (e.g., injected dependency).
        """
        self.session = session

    async def create(self, user:UserEntity) -> UserEntity:
        """
        Persist the given domain UserEntity and return the persisted entity with database-generated fields populated.
        
        Parameters:
            user (UserEntity): Domain user entity to persist.
        
        Returns:
            UserEntity: The persisted user entity with database-generated fields (e.g., id, created_at, updated_at) populated.
        
        Raises:
            DuplicateEmailError: If a user with the same email already exists.
            IntegrityError: Re-raises other integrity violations from the database.
        """
        try:
            # Entity -> ORM Model
            user_model = self._entity_to_model(user)

            # add to Session
            self.session.add(user_model)

            # 刷新以得到db生成的欄位
            await self.session.refresh(user_model)

            # ORM Model -> Entity
            return self._model_to_entity(user_model)
        except IntegrityError as e:
            # rollback
            await self.session.rollback()

            if "email" in str(e.orig):
                raise DuplicateEmailError(f"Email {user.email} already exists")

            raise


    @staticmethod
    def _entity_to_model(entity: UserEntity) -> UserModel:
        """
        Convert a domain UserEntity into a UserModel with corresponding field values.
        
        Parameters:
            entity (UserEntity): Domain user entity to convert.
        
        Returns:
            UserModel: ORM model populated with the entity's id, username, email, password_hash, is_activate, created_at, and updated_at.
        """

        return UserModel(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            password_hash=entity.password_hash,
            is_activate=entity.is_activate,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def _model_to_entity(model:UserModel) -> UserEntity:
        """
        Convert a UserModel ORM instance into a UserEntity domain object.
        
        Parameters:
            model (UserModel): ORM user model to convert.
        
        Returns:
            UserEntity: Domain representation with id, username, email, password_hash, is_activate, created_at, and updated_at populated from the ORM model.
        """

        return UserEntity(
            id=model.id,
            username=model.username,
            email=model.email,
            password_hash=model.password_hash,
            is_activate=model.is_activate,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )