from datetime import UTC, datetime
from uuid import uuid4

from passlib.context import CryptContext

from app.domain.entities.user import User
from app.domain.exceptions.user import UserAlreadyExistsException, UserNotFoundException
from app.ports.input.auth_use_cases import (
    IRegisterUser,
    RegisterUserInput,
    RegisterUserOutput,
)
from app.ports.output.user_repository import IUserRepository

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegisterUser(IRegisterUser):
    def __init__(self, user_repository: IUserRepository) -> None:
        self._user_repository = user_repository

    def _hash(self, password: str) -> str:
        return _pwd.hash(password)

    async def execute(self, data: RegisterUserInput) -> RegisterUserOutput:
        try:
            await self._user_repository.find_by_email(data.email)
        except UserNotFoundException:
            pass
        else:
            raise UserAlreadyExistsException("User with this email already exists")
        now = datetime.now(UTC)
        user = User(
            id=uuid4(),
            email=data.email,
            full_name=data.full_name,
            hashed_password=self._hash(data.password),
            created_at=now,
        )
        saved = await self._user_repository.save(user)
        return RegisterUserOutput(
            id=saved.id,
            email=saved.email,
            full_name=saved.full_name,
            created_at=saved.created_at,
        )
