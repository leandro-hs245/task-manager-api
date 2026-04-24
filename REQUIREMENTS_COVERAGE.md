# Challenge requirements coverage

This file maps the original take-home requirements to what exists in the repository, with paths where they help a reviewer find the code. It also lists what was not implemented relative to the brief.

## Implemented

### Stated stack (Language, API, database, tests, linters, formatters, Docker)

| Requirement | Where |
|------------|--------|
| Python 3.12 (project) | [requirements.txt](requirements.txt), [Dockerfile](Dockerfile) base image `python:3.12` |
| FastAPI | [app/adapters/input/api/main.py](app/adapters/input/api/main.py), routers under [app/adapters/input/api/v1/routers/](app/adapters/input/api/v1/routers/) |
| Real database: PostgreSQL | [docker-compose.yml](docker-compose.yml) `postgres:16-alpine`, async URL with `asyncpg` in [app/adapters/output/db/session.py](app/adapters/output/db/session.py) |
| Migrations | [alembic.ini](alembic.ini), [alembic/env.py](alembic/env.py), [alembic/versions/001_initial_schema.py](alembic/versions/001_initial_schema.py) |
| pytest (unit + integration) | [tests/unit/](tests/unit/), [tests/integration/](tests/integration/), [tests/conftest.py](tests/conftest.py) |
| Coverage floor 75% on the app | [pytest.ini](pytest.ini) `addopts=...--cov=app...--cov-fail-under=75` |
| flake8 | [.flake8](.flake8), [requirements.txt](requirements.txt), [.pre-commit-config.yaml](.pre-commit-config.yaml) |
| black | [pyproject.toml](pyproject.toml) `[tool.black]`, [requirements.txt](requirements.txt) |
| isort | [pyproject.toml](pyproject.toml) `[tool.isort]`, [requirements.txt](requirements.txt) |
| pre-commit (extra workflow, not in the one-page brief) | [.pre-commit-config.yaml](.pre-commit-config.yaml) |
| Dockerfile (multistage) | [Dockerfile](Dockerfile) |
| docker-compose (optional in brief) | [docker-compose.yml](docker-compose.yml) |
| Project description, local and Docker run, tests | [README.md](README.md) |
| Technical decisions | [DECISION_LOG.md](DECISION_LOG.md) (includes architecture and ERD mermaid) |

### 1. Use cases (functional)

| Requirement | Where |
|------------|--------|
| CRUD task lists | Use cases: [app/application/task_list/](app/application/task_list/). HTTP: [app/adapters/input/api/v1/routers/task_list_router.py](app/adapters/input/api/v1/routers/task_list_router.py) |
| CRUD tasks in a list | Use cases: [app/application/task/](app/application/task/). HTTP: [app/adapters/input/api/v1/routers/task_router.py](app/adapters/input/api/v1/routers/task_router.py) |
| Change task status (business rules) | [app/application/task/change_task_status.py](app/application/task/change_task_status.py), domain rules in [app/domain/entities/task.py](app/domain/entities/task.py) and [app/domain/value_objects/status.py](app/domain/value_objects/status.py) |
| List tasks with `status` / `priority` filters and completion % | [app/application/task/list_tasks.py](app/application/task/list_tasks.py), integration: [tests/integration/test_completion_percentage.py](tests/integration/test_completion_percentage.py) |
| **Bonus: JWT, protected routes** | [app/adapters/output/auth/jwt_adapter.py](app/adapters/output/auth/jwt_adapter.py), [app/adapters/input/api/v1/routers/auth_router.py](app/adapters/input/api/v1/routers/auth_router.py), [app/adapters/input/api/v1/dependencies/auth.py](app/adapters/input/api/v1/dependencies/auth.py) |
| **Bonus: assign user to a task** | [app/adapters/output/db/models/task.py](app/adapters/output/db/models/task.py) `assigned_user_id`, [app/application/task/create_task.py](app/application/task/create_task.py) (and update flow) |
| **Bonus: fake email / invitation** | Port [app/ports/output/email_port.py](app/ports/output/email_port.py), adapter [app/adapters/output/email/fake_email_adapter.py](app/adapters/output/email/fake_email_adapter.py) |

### 2. Project structure and quality (layers, Pydantic, errors, tests)

| Requirement | Where |
|------------|--------|
| Clean / layered structure (Domain, application, infrastructure) | [app/domain/](app/domain/) (no framework imports), [app/application/](app/application/) (use cases), [app/adapters/](app/adapters/) and [app/ports/](app/ports/) (hexagonal boundaries; see [DECISION_LOG.md](DECISION_LOG.md)) |
| Pydantic at boundaries | Input port DTOs: [app/ports/input/](app/ports/input/). API schemas: [app/adapters/input/api/v1/schemas/](app/adapters/input/api/v1/schemas/) |
| Custom domain exceptions and HTTP mapping | [app/domain/exceptions/](app/domain/exceptions/), mapping in [app/adapters/input/api/main.py](app/adapters/input/api/main.py) |
| Business validations | Status transitions, ownership checks, and related rules in domain and use cases (see [DECISION_LOG.md](DECISION_LOG.md) and tests under [tests/](tests/)) |
| Unit and integration tests with pytest | [tests/unit/](tests/unit/) and [tests/integration/](tests/integration/) |

### 3. Configuration files named in the brief

| File | Path |
|------|------|
| `pytest.ini` | [pytest.ini](pytest.ini) |
| `.flake8` | [.flake8](.flake8) |

## Not made (relative to the brief) or out of scope

- **Ruff** The handout lists *flake8* or *pylint* for linting, and in one line also mentions ruff with flake8 for project structure. This repository uses **flake8** (plus black and isort) and does **not** add a **ruff** configuration or hook. The stated minimum is met with flake8.
- **unittest** The requirement allows pytest *or* unittest. Only **pytest** is used; there is no parallel unittest suite.
- **Cloud CI (GitHub Actions, GitLab CI, etc.)** There is no `.github/workflows` (or similar) pipeline in the repo. Local **pre-commit** and **pytest** are documented in [README.md](README.md); automation in a remote host is not part of the deliverable.
- **Real email delivery (SMTP, providers)** The exercise asked for a **fictional** notification; there is no production mail integration, by design ([app/adapters/output/email/fake_email_adapter.py](app/adapters/output/email/fake_email_adapter.py)).
