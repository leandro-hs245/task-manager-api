import os
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from uuid import uuid4

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

os.environ.setdefault("SECRET_KEY", "a" * 32)
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("CORS_ALLOW_ORIGINS", "*")

from app.adapters.input.api.main import app  # noqa: E402
from app.adapters.input.api.v1.dependencies import auth as auth_dep  # noqa: E402
from app.adapters.output.db import session as session_mod  # noqa: E402
from app.adapters.output.db.models import UserModel  # noqa: E402
from app.adapters.output.db.session import Base  # noqa: E402
from app.domain.entities.user import User  # noqa: E402

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest_asyncio.fixture
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    await session_mod.dispose_engine()
    e = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_mod._engine = e  # type: ignore[attr-defined]
    session_mod._session_maker = async_sessionmaker(  # type: ignore[attr-defined]
        e,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with e.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield e
    finally:
        app.dependency_overrides.clear()
        await session_mod.dispose_engine()


@pytest_asyncio.fixture
async def test_session(
    test_engine: AsyncEngine,  # noqa: ARG001
) -> AsyncGenerator[AsyncSession, None]:
    sm = session_mod.get_session_maker()
    async with sm() as s:
        yield s


@pytest_asyncio.fixture
async def sample_user(test_session: AsyncSession) -> User:
    now = datetime.now(UTC)
    uid = uuid4()
    m = UserModel(
        id=uid,
        email=f"u{uid.hex[:8]}@t.com",
        full_name="Test",
        hashed_password=_pwd.hash("pass"),
        created_at=now,
    )
    test_session.add(m)
    await test_session.commit()
    return User(
        id=m.id,
        email=m.email,
        full_name=m.full_name,
        hashed_password=m.hashed_password,
        created_at=m.created_at,
    )


@pytest_asyncio.fixture
async def test_client(
    test_engine: AsyncEngine,  # noqa: ARG001
    sample_user: User,
) -> AsyncGenerator[AsyncClient, None]:

    async def _as_user() -> User:
        return sample_user

    app.dependency_overrides[auth_dep.get_current_user] = _as_user
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport, base_url="http://test", timeout=30.0
        ) as ac:
            yield ac
    finally:
        if auth_dep.get_current_user in app.dependency_overrides:
            del app.dependency_overrides[auth_dep.get_current_user]


@pytest_asyncio.fixture
async def anon_client(
    test_engine: AsyncEngine,  # noqa: ARG001
) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", timeout=30.0
    ) as ac:
        yield ac
