from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.output.db.models.user import UserModel
from app.domain.entities.user import User
from app.domain.exceptions.user import UserNotFoundException
from app.ports.output.user_repository import IUserRepository


class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def to_domain(m: UserModel) -> User:
        return User(
            id=m.id,
            email=m.email,
            full_name=m.full_name,
            hashed_password=m.hashed_password,
            created_at=m.created_at,
        )

    @staticmethod
    def to_orm(e: User) -> UserModel:
        return UserModel(
            id=e.id,
            email=e.email,
            full_name=e.full_name,
            hashed_password=e.hashed_password,
            created_at=e.created_at,
        )

    async def save(self, user: User) -> User:
        m = self.to_orm(user)
        self._session.add(m)
        await self._session.flush()
        return self.to_domain(m)

    async def find_by_id(self, user_id: UUID) -> User:
        m = await self._session.get(UserModel, user_id)
        if m is None:
            raise UserNotFoundException("User not found")
        return self.to_domain(m)

    async def find_by_email(self, email: str) -> User:
        q = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        m = q.scalar_one_or_none()
        if m is None:
            raise UserNotFoundException("User not found")
        return self.to_domain(m)

    async def update(self, user: User) -> User:
        m = await self._session.get(UserModel, user.id)
        if m is None:
            raise UserNotFoundException("User not found")
        m.email = user.email
        m.full_name = user.full_name
        m.hashed_password = user.hashed_password
        m.created_at = user.created_at
        await self._session.flush()
        return self.to_domain(m)

    async def delete(self, user_id: UUID) -> None:
        m = await self._session.get(UserModel, user_id)
        if m is None:
            raise UserNotFoundException("User not found")
        await self._session.delete(m)
        await self._session.flush()
