from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.input.api.v1.schemas.user import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.adapters.output.auth.jwt_adapter import JWTAdapter
from app.adapters.output.db.repositories.user_repository import (
    SQLAlchemyUserRepository,
)
from app.adapters.output.db.session import get_db
from app.application.auth.login_user import LoginUser
from app.application.auth.register_user import RegisterUser
from app.ports.input.auth_use_cases import LoginUserInput, RegisterUserInput

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    body: UserRegister,
    session: AsyncSession = Depends(get_db),
) -> UserResponse:
    use_case = RegisterUser(SQLAlchemyUserRepository(session))
    out = await use_case.execute(
        RegisterUserInput(
            email=body.email,
            full_name=body.full_name,
            password=body.password,
        )
    )
    return UserResponse(
        id=out.id,
        email=out.email,
        full_name=out.full_name,
        created_at=out.created_at,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: UserLogin,
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    use_case = LoginUser(
        SQLAlchemyUserRepository(session), JWTAdapter()
    )
    out = await use_case.execute(
        LoginUserInput(email=body.email, password=body.password)
    )
    return TokenResponse(
        access_token=out.access_token, token_type=out.token_type
    )
