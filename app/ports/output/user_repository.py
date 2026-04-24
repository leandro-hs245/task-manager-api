from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.user import User


class IUserRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> User: ...

    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> User: ...

    @abstractmethod
    async def find_by_email(self, email: str) -> User: ...

    @abstractmethod
    async def update(self, user: User) -> User: ...

    @abstractmethod
    async def delete(self, user_id: UUID) -> None: ...
