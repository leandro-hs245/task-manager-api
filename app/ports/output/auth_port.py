from abc import ABC, abstractmethod
from uuid import UUID


class IAuthPort(ABC):
    @abstractmethod
    def create_token(self, user_id: UUID) -> str: ...

    @abstractmethod
    def verify_token(self, token: str) -> UUID: ...
