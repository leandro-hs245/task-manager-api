# Task Manager API

REST API for managing task lists and tasks, with optional assignment, email simulation, and JWT-based authentication. Built as a technical challenge in **Python 3.12** with **FastAPI**, **PostgreSQL (async)**, **SQLAlchemy 2.0**, **pytest**, and **Docker**.

## Features

- **Task lists** — create, list (owner-scoped), get, update, and delete; each list exposes a **completion percentage** (done / total for all tasks in the list).
- **Tasks** — create, list (with optional `status` and `priority` query filters), get, update, delete, and **PATCH** status with validated transitions: `pending` → `in_progress` → `done` or `in_progress` → `pending`.
- **Users & auth** — register, login, JWT bearer tokens, protected list/task routes.
- **Assignment** — assign a user to a task; **synchronous** fake “email” returns a `notification` object on create; **async** fake path is logging-only.
- **Quality** — `flake8`, `black`, `isort`, pytest with **75%+** line coverage, Alembic migrations, multi-stage **Docker** image, **docker-compose** with PostgreSQL 16 and health checks.

## Architecture (hexagonal / ports & adapters)

- **Domain** — entities, value objects (`TaskStatus`, `TaskPriority`), and `BaseDomainException` and subclasses. No framework imports.
- **Application** — use cases (task list, task, auth) depend only on **port** interfaces and the domain; UUIDs and timestamps are created in use cases for writes.
- **Ports** — **input** (use case + Pydantic DTOs) and **output** (repositories, `IEmailPort`, `IAuthPort`); implemented by adapters.
- **Adapters** — **driving** FastAPI under `app/adapters/input/api/`, **driven** async SQLAlchemy repositories, `FakeEmailAdapter`, `JWTAdapter` under `app/adapters/output/`.

## Prerequisites

- **Python 3.12** (the project is tested on 3.12; 3.14+ may need dependency wheels adjusted).
- **Docker** and **Docker Compose** (recommended for PostgreSQL; local Postgres also works).
- (Optional) **flake8** / **black** / **isort** in your venv for lint/format.

## Local setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set DATABASE_URL to a running Postgres, e.g.:
#   postgresql+asyncpg://USER:PASS@localhost:5432/DBNAME
# Set SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, and Postgres vars to match
export $(grep -v '^#' .env | xargs)  # or use direnv
alembic upgrade head
uvicorn app.adapters.input.api.main:app --reload --host 0.0.0.0 --port 8000
```

- API base: `http://127.0.0.1:8000` — OpenAPI docs: `/docs` (FastAPI may mount these at root).

## Docker

```bash
cp .env.example .env
# In .env, set POSTGRES_*, and ensure DATABASE_URL for the *api* service is overridden by
#   compose (see docker-compose.yml) to postgresql+asyncpg://...@db:5432/...
docker compose up --build
```

The `api` service runs `alembic upgrade head` then `uvicorn` on port `8000`. The `db` service uses a named volume and a health check so the API starts after PostgreSQL is ready.

## Tests

```bash
source .venv/bin/activate
pytest
```

Coverage is configured in `pytest.ini` with `pytest-cov` and **`--cov-fail-under=75`**. The suite includes unit tests (fakes) and async integration tests (HTTPX + ASGI) with a shared SQLite in-memory engine for speed.

## Environment variables

| Variable | Purpose |
|----------|--------|
| `DATABASE_URL` | Async URL, e.g. `postgresql+asyncpg://user:pass@host:5432/db` |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT` | Used by `docker-compose` and documented for local/dev parity |
| `SECRET_KEY` | HMAC key for JWT signing (required in production) |
| `ALGORITHM` | JWT algorithm (default `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime |
| `CORS_ALLOW_ORIGINS` | Comma-separated list or `*` (default `*`) |
| `SQLALCHEMY_ECHO` | Set to `true` to log SQL (optional) |

## API summary (prefix `/api/v1`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | no | Create user (201) |
| POST | `/auth/login` | no | Return JWT (200) |
| GET/POST/GET/PUT/DELETE | `/lists` … | yes | List CRUD, list index returns per-list completion % |
| GET/POST/GET/PUT/DELETE | `/lists/{id}/tasks` … | yes | Task CRUD; `GET` returns `{ tasks, completion_percentage }` |
| PATCH | `/lists/{id}/tasks/{id}/status` | yes | Change status with business rules (422 on invalid) |

All protected routes expect `Authorization: Bearer <token>`.

