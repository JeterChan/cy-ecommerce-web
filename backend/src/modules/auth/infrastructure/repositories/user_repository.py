from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from sqlalchemy.exc import IntegrityError

from modules.auth.domain.repositories.i_user_repository import IUserRepository
from modules.auth.domain.entity import UserEntity
from modules.auth.infrastructure.models.user import UserModel
from core.exceptions import DuplicateEmailError

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
        init repository
        :param session: SQLAlchemy 異步 Session (由 FastAPI Dependency 注入)
        """
        self.session = session

    async def create(self, user:UserEntity) -> UserEntity:
        try:
            # Entity -> ORM Model
            user_model = self._entity_to_model(user)

            # add to Session
            self.session.add(user_model)

            await self.session.commit()

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

    async def exists_by_email(self, email:str) -> bool:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return user is not None

    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        """
        根據 email 查詢使用者

        Args:
            email: 使用者電子郵件

        Returns:
            User Entity 或 None（如果不存在）
        """
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()

        if user_model is None:
            return None

        return self._model_to_entity(user_model)

    @staticmethod
    def _entity_to_model(entity: UserEntity) -> UserModel:
        """
        Entity -> ORM Model 轉換
        """

        return UserModel(
            id=entity.id,
            username=entity.username,
            email=str(entity.email),  # EmailStr -> str
            password_hash=entity.password_hash,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def _model_to_entity(model:UserModel) -> UserEntity:
        """
        ORM Model -> Entity
        Pydantic 會自動驗證並轉換 str 為 EmailStr
        """

        return UserEntity(
            id=model.id,
            username=model.username,
            email=model.email,  # type: ignore[arg-type]  # Pydantic 自動處理 str -> EmailStr
            password_hash=model.password_hash,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )