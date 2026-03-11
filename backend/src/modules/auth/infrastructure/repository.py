from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
from sqlalchemy.exc import IntegrityError

from modules.auth.domain.repository import IUserRepository
from modules.auth.domain.entities import UserEntity
from modules.auth.infrastructure.models import UserModel
from core.exceptions import DuplicateEmailError, UserNotFoundError

class UserRepository(IUserRepository):
    """
    使用者資料存取層實作 (SQLAlchemy)

    職責：
    - 實作 IUserRepository Interface
    - 處理 Domain Entity 與 ORM Model 的轉換
    - 管理 SQLAlchemy Session
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: UserEntity) -> UserEntity:
        try:
            user_model = self._entity_to_model(user)
            self.session.add(user_model)
            await self.session.commit()
            await self.session.refresh(user_model)
            return self._model_to_entity(user_model)
        except IntegrityError as e:
            await self.session.rollback()
            if "email" in str(e.orig):
                raise DuplicateEmailError(f"Email {user.email} already exists")
            raise

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(UserModel).where(
            and_(UserModel.email == email, UserModel.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def exists_by_username(self, username: str) -> bool:
        stmt = select(UserModel).where(
            and_(UserModel.username == username, UserModel.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_by_id(self, user_id) -> Optional[UserEntity]:
        stmt = select(UserModel).where(
            and_(UserModel.id == user_id, UserModel.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return self._model_to_entity(user_model) if user_model else None

    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        stmt = select(UserModel).where(
            and_(UserModel.email == email, UserModel.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return self._model_to_entity(user_model) if user_model else None

    async def get_by_username(self, username: str) -> Optional[UserEntity]:
        stmt = select(UserModel).where(
            and_(UserModel.username == username, UserModel.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return self._model_to_entity(user_model) if user_model else None

    async def update(self, user: UserEntity) -> UserEntity:
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user is None:
            raise UserNotFoundError(f"使用者不存在 (id: {user.id})")

        # 更新欄位
        existing_user.username = user.username
        existing_user.email = str(user.email)
        existing_user.password_hash = user.password_hash
        existing_user.is_active = user.is_active
        existing_user.is_verified = user.is_verified
        existing_user.phone = user.phone
        existing_user.address = user.address
        existing_user.carrier_type = user.carrier_type
        existing_user.carrier_number = user.carrier_number
        existing_user.tax_id = user.tax_id
        existing_user.deleted_at = user.deleted_at

        await self.session.commit()
        await self.session.refresh(existing_user)
        return self._model_to_entity(existing_user)

    @staticmethod
    def _entity_to_model(entity: UserEntity) -> UserModel:
        return UserModel(
            id=entity.id,
            username=entity.username,
            email=str(entity.email),
            password_hash=entity.password_hash,
            is_active=entity.is_active,
            is_verified=entity.is_verified,
            phone=entity.phone,
            address=entity.address,
            carrier_type=entity.carrier_type,
            carrier_number=entity.carrier_number,
            tax_id=entity.tax_id,
            deleted_at=entity.deleted_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def _model_to_entity(model: UserModel) -> UserEntity:
        return UserEntity(
            id=model.id,
            username=model.username,
            email=model.email,  # type: ignore[arg-type]
            password_hash=model.password_hash,
            is_active=model.is_active,
            is_verified=model.is_verified,
            phone=model.phone,
            address=model.address,
            carrier_type=model.carrier_type,
            carrier_number=model.carrier_number,
            tax_id=model.tax_id,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
