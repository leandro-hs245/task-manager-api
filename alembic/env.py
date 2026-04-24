import os
import sys
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.adapters.output.db.models import (  # noqa: E402
    TaskListModel,
    TaskModel,
    UserModel,
)
from app.adapters.output.db.session import Base  # noqa: E402

if False:  # appease linters: models imported for side effects on Base.metadata
    UserModel, TaskListModel, TaskModel

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_sync_url() -> str:
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        msg = "DATABASE_URL is required for migrations"
        raise RuntimeError(msg)
    return url.replace("postgresql+asyncpg", "postgresql+psycopg")


def run_migrations_offline() -> None:
    context.configure(
        url=get_sync_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        get_sync_url(),
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
