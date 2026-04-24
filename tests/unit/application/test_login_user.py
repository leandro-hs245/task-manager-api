import pytest
from datetime import UTC, datetime
from uuid import uuid4

from app.application.auth.login_user import LoginUser
from app.domain.exceptions.user import InvalidCredentialsException
from app.domain.entities.user import User
from app.ports.input.auth_use_cases import LoginUserInput
from tests.fakes import InMemoryUserRepository, _FakeAuth
from passlib.context import CryptContext

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.mark.asyncio
async def test_login_success() -> None:
    ur = InMemoryUserRepository()
    uid = uuid4()
    now = datetime.now(UTC)
    u = User(
        id=uid,
        email="e@x.com",
        full_name="E",
        hashed_password=_pwd.hash("good"),
        created_at=now,
    )
    await ur.save(u)
    uc = LoginUser(ur, _FakeAuth())
    out = await uc.execute(
        LoginUserInput(email="e@x.com", password="good")
    )
    assert out.access_token
    assert out.token_type == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password() -> None:
    ur = InMemoryUserRepository()
    uid = uuid4()
    now = datetime.now(UTC)
    u = User(
        id=uid,
        email="e2@x.com",
        full_name="E",
        hashed_password=_pwd.hash("good"),
        created_at=now,
    )
    await ur.save(u)
    uc = LoginUser(ur, _FakeAuth())
    with pytest.raises(InvalidCredentialsException):
        await uc.execute(
            LoginUserInput(email="e2@x.com", password="bad")
        )


@pytest.mark.asyncio
async def test_login_unknown_email() -> None:
    ur = InMemoryUserRepository()
    uc = LoginUser(ur, _FakeAuth())
    with pytest.raises(InvalidCredentialsException):
        await uc.execute(
            LoginUserInput(email="none@x.com", password="x")
        )
