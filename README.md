# Task Manager API

REST API for task lists and tasks, built for a backend technical challenge. The service implements CRUD for lists and tasks, status rules, optional task assignment, simulated email notifications, and JWT-protected routes. The stack is **Python 3.12**, **FastAPI**, **PostgreSQL** (via **asyncpg**), **SQLAlchemy 2.0** (async), **Alembic**, **Pydantic**, **pytest**, and **Docker**.

## Project description

The API allows authenticated users to manage their own task lists and the tasks within each list. A list summary can include a **completion percentage** (ratio of tasks in the `done` state to the total number of tasks in that list, expressed as a percentage; empty lists report `0.0%`). Tasks support filtering by `status` and `priority` when listing, and status changes follow explicit transitions validated in the domain layer.

**Implemented scope (challenge alignment):**

| Area | What is included |
|------|------------------|
| Core | CRUD for task lists; CRUD for tasks under a list; change task status with validated transitions; list tasks with optional filters and completion metadata |
| Optional / bonus | JWT auth (register, login, Bearer protection on list/task routes); assign a user to a task; fake email port (sync returns a notification payload, async only logs) |
| Quality | Hexagonal layout (domain, application, ports, adapters), custom domain exceptions, `flake8` + `black` + `isort`, `pytest` with at least 75% line coverage on `app/`, `pytest.ini`, multistage `Dockerfile`, `docker-compose` with PostgreSQL, pre-commit hooks (linters on commit, tests on push) |

## Architecture

The codebase follows **hexagonal (ports and adapters) / clean architecture** guidelines from the challenge:

- **Domain**: entities, value objects (`TaskStatus`, `TaskPriority`), and `BaseDomainException` and subclasses. No web framework, ORM, or Pydantic imports in the domain.
- **Application**: use cases for task lists, tasks, and auth. They depend on port interfaces and the domain only. Identifiers and timestamps for writes are created in use cases as required by the spec.
- **Ports**: **input** ports express use case contracts with Pydantic DTOs; **output** ports define `ITaskRepository`, `ITaskListRepository`, `IUserRepository`, `IEmailPort`, and `IAuthPort`.
- **Adapters**: **driving** adapter is FastAPI (routers, dependencies, Pydantic API schemas) under `app/adapters/input/api/`. **Driven** adapters include async SQLAlchemy repositories, `FakeEmailAdapter`, and `JWTAdapter` under `app/adapters/output/`.

Repository layout: `app/domain`, `app/application`, `app/ports`, `app/adapters`, and `tests/unit` and `tests/integration`.

## Prerequisites

- **Python 3.12** (the project is tested on 3.12; other versions may need dependency pins reviewed).
- **Docker** and **Docker Compose** plugin (`docker compose`) to run the full stack without a local PostgreSQL install.
- A local **PostgreSQL** instance is optional if you run the API and Alembic on the host instead of in Docker.

## Local environment setup

1. **Clone** the repository and open a shell at the project root.

2. **Virtual environment and dependencies**

   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configuration**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set at least `DATABASE_URL` (pointing to your local PostgreSQL, for example `postgresql+asyncpg://USER:PASS@localhost:5432/DBNAME`), the `POSTGRES_*` fields if you use them for your own setup, and `SECRET_KEY` (and optionally `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `CORS_ALLOW_ORIGINS`). The application reads configuration from the environment (see [Environment variables](#environment-variables)).

4. **Migrations and run**

   Load env vars in your shell if needed (or use a tool like `direnv`):

   ```bash
   set -a && source .env && set +a
   # or: export $(grep -v '^#' .env | xargs)
   alembic upgrade head
   uvicorn app.adapters.input.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

- Base URL: `http://127.0.0.1:8000`  
- Interactive API docs: `http://127.0.0.1:8000/docs` (Swagger UI)  
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Running the application in Docker

1. **Prepare `.env`**

   ```bash
   cp .env.example .env
   ```

   Set `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` (and a strong `SECRET_KEY`). The Compose file [docker-compose.yml](docker-compose.yml) **overrides** `DATABASE_URL` for the `api` service to use the `db` service hostname, so the API points at the bundled PostgreSQL. You do not need to hand-edit that URL for Docker in normal use.

2. **Start**

   ```bash
   docker compose up --build
   ```

- The `db` service is **postgres:16-alpine** with a named volume and a health check.
- The `api` service waits for the database to be healthy, runs `alembic upgrade head`, then runs Uvicorn on `0.0.0.0:8000`.
- Map `8000:8000` so you can open `http://localhost:8000/docs` on the host.

3. **Stop**

   - Foreground: `Ctrl+C`  
- Detached: `docker compose down` (add `-v` to remove the Postgres volume and wipe data)

## Tests

**Run tests (with the same options as in CI and pre-commit push hook):**

```bash
source .venv/bin/activate
pytest
```

- Configuration lives in [pytest.ini](pytest.ini): `testpaths = tests`, `pythonpath = .`, `asyncio_mode = auto`, `asyncio_default_fixture_loop_scope = function`, and `addopts` with `--cov=app --cov-report=term-missing --cov-fail-under=75`.  
- **Unit** tests use in-memory fakes. **Integration** tests call the app via `httpx` and an in-memory **SQLite** engine with **aiosqlite** (see [tests/conftest.py](tests/conftest.py)).  
- To see verbose test names: `pytest -v`

## Linting and formatting

- **Linter**: [Flake8](.flake8), max line length 88, ignores E203 and W503 (compatibility with Black).  
- **Formatters**: [Black](pyproject.toml) and [isort](pyproject.toml) (`profile = "black"`, line length 88).  
- Run manually: `flake8 app`, `black .`, `isort .` (or rely on pre-commit, below).

## Git hooks (pre-commit)

The file [.pre-commit-config.yaml](.pre-commit-config.yaml) is configured with:

- **On `git commit`**: Black, isort, and Flake8.  
- **On `git push`**: `python -m pytest -v` with `verbose: true` on the hook so you see full pytest and coverage output (pre-commit usually hides success output without this).  

**Setup (once, with a venv that has project dependencies):**

```bash
source .venv/bin/activate
pip install -r requirements.txt
pre-commit install
```

`default_install_hook_types` includes `pre-commit` and `pre-push`, so a single `pre-commit install` registers both hook types. Dry run: `pre-commit run --all-files` and `pre-commit run --hook-stage pre-push --all-files`.

If you commit from a GUI that does not inherit your venv, ensure `python` on `PATH` can import `pytest` and the app, or use a terminal with `.venv` activated.

## Environment variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Async SQLAlchemy URL, e.g. `postgresql+asyncpg://user:pass@host:5432/db`. Overridden in Docker Compose for the `api` service. |
| `POSTGRES_USER` | PostgreSQL user (used by Compose for the `db` service and interpolated for `DATABASE_URL` in compose). |
| `POSTGRES_PASSWORD` | PostgreSQL password. |
| `POSTGRES_DB` | Database name. |
| `POSTGRES_HOST` | Documented for local tools; the app in Docker does not use this to build the URL. |
| `POSTGRES_PORT` | Documented for local tools. |
| `SECRET_KEY` | HMAC key for signing JWTs (set a long random value in all non-local deployments). |
| `ALGORITHM` | JWT algorithm (default `HS256`). |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime. |
| `CORS_ALLOW_ORIGINS` | Comma-separated list or `*`. |
| `SQLALCHEMY_ECHO` | Set to `true` to log SQL (optional, debugging). |

## API overview (base path `/api/v1`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | no | Create user. Returns 201. |
| POST | `/auth/login` | no | Return access token. Returns 200. |
| POST | `/lists` | yes | Create task list. |
| GET | `/lists` | yes | List current user's task lists (with per-list completion percentage). |
| GET | `/lists/{list_id}` | yes | Get one list. |
| PUT | `/lists/{list_id}` | yes | Update a list. |
| DELETE | `/lists/{list_id}` | yes | Delete a list. 204. |
| POST | `/lists/{list_id}/tasks` | yes | Create task. Optional `assigned_user_id` and fake email notification in response. |
| GET | `/lists/{list_id}/tasks` | yes | List tasks. Query: `status`, `priority` (optional). Returns JSON with `tasks` and `completion_percentage`. |
| GET | `/lists/{list_id}/tasks/{task_id}` | yes | Get one task. |
| PUT | `/lists/{list_id}/tasks/{task_id}` | yes | Update task. |
| DELETE | `/lists/{list_id}/tasks/{task_id}` | yes | Delete task. 204. |
| PATCH | `/lists/{list_id}/tasks/{task_id}/status` | yes | Change status (422 on invalid transition). |

Authenticated routes expect `Authorization: Bearer <access_token>`. Domain errors are mapped to HTTP status codes in [app/adapters/input/api/main.py](app/adapters/input/api/main.py) with a JSON body `{ "detail": "..." }`.

## Further reading

Technical trade-offs and rationale are recorded in [DECISION_LOG.md](DECISION_LOG.md).

A Postman collection for all challenge use cases (variables: `baseUrl`, `accessToken`, plus scripts for `registerEmail`, `userId`, `listId`, `taskId`) is in [postman/Task-Manager-API.postman_collection.json](postman/Task-Manager-API.postman_collection.json). Import it in Postman or Insomnia (as a collection import if supported).
