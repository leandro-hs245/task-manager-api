import pytest

from app.application.auth.register_user import RegisterUser
from app.domain.exceptions.user import UserAlreadyExistsException
from app.ports.input.auth_use_cases import RegisterUserInput
from tests.fakes import InMemoryUserRepository


@pytest.mark.asyncio
async def test_register_success() -> None:
    ur = InMemoryUserRepository()
    uc = RegisterUser(ur)
    out = await uc.execute(
        RegisterUserInput(
            email="new@x.com", full_name="N", password="password123"
        )
    )
    assert out.email == "new@x.com"
    u = await ur.find_by_email("new@x.com")
    assert u.hashed_password != "password123"


@pytest.mark.asyncio
async def test_register_duplicate() -> None:
    ur = InMemoryUserRepository()
    uc = RegisterUser(ur)
    await uc.execute(
        RegisterUserInput(
            email="d@x.com", full_name="A", password="p"
        )
    )
    with pytest.raises(UserAlreadyExistsException):
        await uc.execute(
            RegisterUserInput(
                email="d@x.com", full_name="B", password="p2"
            )
        )
