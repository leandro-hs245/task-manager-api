from passlib.context import CryptContext
from app.domain.exceptions.user import (
    InvalidCredentialsException,
    UserNotFoundException,
)
from app.ports.input.auth_use_cases import ILoginUser, LoginUserInput, LoginUserOutput
from app.ports.output.auth_port import IAuthPort
from app.ports.output.user_repository import IUserRepository

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginUser(ILoginUser):
    def __init__(
        self, user_repository: IUserRepository, auth_port: IAuthPort
    ) -> None:
        self._user_repository = user_repository
        self._auth_port = auth_port

    async def execute(self, data: LoginUserInput) -> LoginUserOutput:
        try:
            user = await self._user_repository.find_by_email(data.email)
        except UserNotFoundException as e:
            raise InvalidCredentialsException("Invalid credentials") from e
        if not _pwd.verify(data.password, user.hashed_password):
            raise InvalidCredentialsException("Invalid credentials")
        token = self._auth_port.create_token(user.id)
        return LoginUserOutput(access_token=token, token_type="bearer")
