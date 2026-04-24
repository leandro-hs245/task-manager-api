import os
from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt

from app.domain.exceptions.user import InvalidCredentialsException
from app.ports.output.auth_port import IAuthPort


class JWTAdapter(IAuthPort):
    def __init__(self) -> None:
        self._secret = os.environ.get("SECRET_KEY")
        self._algorithm = os.environ.get("ALGORITHM", "HS256")
        raw = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        self._expire_minutes = int(raw)

    def create_token(self, user_id: UUID) -> str:
        if not self._secret:
            msg = "SECRET_KEY is not set"
            raise RuntimeError(msg)
        expire = datetime.now(UTC) + timedelta(minutes=self._expire_minutes)
        payload = {
            "sub": str(user_id),
            "exp": expire,
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def verify_token(self, token: str) -> UUID:
        if not self._secret:
            msg = "SECRET_KEY is not set"
            raise RuntimeError(msg)
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            sub = payload.get("sub")
            if not sub:
                raise InvalidCredentialsException("Invalid token")
            return UUID(sub)
        except (JWTError, ValueError) as e:
            raise InvalidCredentialsException("Invalid or expired token") from e
