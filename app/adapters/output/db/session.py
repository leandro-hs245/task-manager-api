import os
from collections.abc import AsyncGenerator
from typing import Any

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

_engine: AsyncEngine | None = None
_session_maker: async_sessionmaker[AsyncSession] | None = None


def _get_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        msg = "DATABASE_URL environment variable is not set"
        raise RuntimeError(msg)
    return url


def get_engine() -> AsyncEngine:
    global _engine, _session_maker
    if _engine is None:
        _engine = create_async_engine(
            _get_database_url(),
            echo=os.environ.get("SQLALCHEMY_ECHO", "").lower() == "true",
        )
        _session_maker = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    if _session_maker is None:
        get_engine()
    return _session_maker  # type: ignore[return-value]


async def dispose_engine() -> None:
    global _engine, _session_maker
    e = _engine
    if e is not None:
        await e.dispose()
    _engine = None
    _session_maker = None


class Base(DeclarativeBase):
    pass


AnyModel = Any


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Request-scoped session; commit on success, rollback on error."""
    maker = get_session_maker()
    async with maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:  # noqa: BLE001
            await session.rollback()
            raise
