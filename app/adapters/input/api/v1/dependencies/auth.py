from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.output.auth.jwt_adapter import JWTAdapter
from app.adapters.output.db.repositories.user_repository import (
    SQLAlchemyUserRepository,
)
from app.adapters.output.db.session import get_db
from app.domain.entities.user import User
from app.domain.exceptions.user import (
    InvalidCredentialsException,
    UserNotFoundException,
)

bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: AsyncSession = Depends(get_db),
) -> User:
    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    auth = JWTAdapter()
    try:
        user_id = auth.verify_token(creds.credentials)
    except InvalidCredentialsException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.message),
        ) from e
    repo = SQLAlchemyUserRepository(session)
    try:
        return await repo.find_by_id(user_id)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        ) from e
