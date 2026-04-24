# Decision log

This document records the main technical choices for the Task Manager API and how they meet the challenge goals: clear boundaries, testability, async performance, and maintainable operations.

## Hexagonal architecture (ports and adapters)

The project uses **hexagonal (ports and adapters) layout** so the core stays independent from HTTP, the database, email, and JWT details.

- **Domain** holds entities, value objects, and custom exceptions. It has no imports from FastAPI, SQLAlchemy, or Pydantic, so business rules stay pure and easy to reason about in isolation.
- **Application** use cases orchestrate work and depend only on **output port** interfaces (repositories, email, auth), not on concrete drivers.
- **Input ports** describe what the API layer must call; they use Pydantic DTOs at the boundary. **Output ports** describe what the application needs from the outside (persist users, lists, and tasks, send fake mail, sign and verify tokens).

**Why this helps**

- **Swappable adapters**: you can replace PostgreSQL with another store or change how JWT is issued without touching domain or use case code, as long as the port contract stays the same.
- **Email as a port**: the challenge asks for a mock notification, not a real SMTP stack. The `IEmailPort` is implemented by a small **FakeEmailAdapter**; a real provider would implement the same interface later.
- **Testability**: unit tests use in-memory fakes for repositories and ports. Integration tests hit the HTTP layer with a test database, so both fast feedback and end-to-end behavior are covered.

## FastAPI instead of Flask or Django

**FastAPI** was chosen because this challenge specifies it, and it fits the design well: native `async` routes line up with async repositories, dependency injection is explicit (for example `get_current_user` and repository wiring), and OpenAPI plus automatic request/response validation reduce boilerplate compared to manual Flask patterns.

Django is excellent for full-stack or admin-heavy projects; here a thin API with strict layering is easier to keep aligned with domain-driven folders. Flask could work, but you would add more structure by hand for async DB access and validation.

## PostgreSQL with asyncpg

**PostgreSQL** is the real database. The **asyncpg** driver is used with SQLAlchemy’s async engine so that database I/O does not block the event loop in async route handlers. That keeps latency predictable under concurrent requests and matches the async use case and repository methods.

## Async SQLAlchemy 2.0

**SQLAlchemy 2.0** style (select/update/delete constructs, `AsyncSession`, async engine) is used in repository adapters. The **application layer** stays free of ORM details; only the output adapters map between domain entities and rows.

**Alembic** runs in a **synchronous** context: the migration env [alembic/env.py](alembic/env.py) rewrites the app’s `DATABASE_URL` by replacing `postgresql+asyncpg` with `postgresql+psycopg` for the sync migration engine, while the running app keeps `postgresql+asyncpg` for async I/O. That split is a common pattern: one tool for schema evolution, another for the async runtime.

## Fake email adapter: sync vs async

The `IEmailPort` contract has two methods.

- **Synchronous** `send_invitation_sync` returns a `NotificationResult` so the use case can attach a concrete payload to the HTTP response when a task is created with an assignee (the challenge requires simulating an invitation without sending real email).
- **Asynchronous** `send_invitation_async` returns `None` and is used for a **fire-and-forget** path; the fake implementation only logs, so you can show both code paths without a mail server.

The adapter lives in infrastructure, so a future real implementation can keep the same port and swap behavior.

## JWT with python-jose

**python-jose** issues and validates JWTs with `SECRET_KEY`, `ALGORITHM`, and expiry, using standard `sub` and `exp` claims. It is lightweight for a take-home scope and keeps auth logic in a small **adapters** class behind an auth-related port or dependency, instead of pulling in a large framework.

Invalid or expired tokens are rejected in the FastAPI dependency that resolves the current user, which maps to **401** and the appropriate domain or HTTP handling.

## Task status transitions

Status changes are **not** free-form updates: the domain enforces a small state machine so “done” and “in progress” mean something consistent in reports and in the completion percentage.

Allowed transitions:

- `pending` to `in_progress` (start work)
- `in_progress` to `done` (complete)
- `in_progress` to `pending` (roll back or pause)

Anything else raises `InvalidTaskStatusTransitionException` and is exposed as **422** to the client. This avoids invalid jumps (for example `pending` straight to `done` without an “in progress” step) and keeps the rule list small and testable.

## Password hashing with bcrypt

**passlib** with the **bcrypt** backend hashes passwords on registration; login uses a constant-time verify. A **bcrypt** version compatible with `passlib` is pinned in `requirements.txt` so local runs, CI, and Docker do not hit runtime compatibility issues.

## Docker and Compose

A **multistage Dockerfile** keeps the final image smaller by building dependencies in one stage and copying only what the runtime needs. **docker-compose** runs **PostgreSQL 16** with a health check, then starts the API after `alembic upgrade head` so a new clone can run with one command. The `api` service **overrides** `DATABASE_URL` in the compose file to point at the `db` host, so developers do not have to hand-edit the URL for the container network.

## Tooling: flake8, black, isort, pre-commit, pytest

The challenge requires **flake8** as the linter, **black** for formatting, and a **.flake8** file with project-specific ignores (for example E203 and W503 for Black compatibility). **isort** keeps import order consistent with Black.

**pre-commit** runs formatters and the linter on **commit** and **pytest** on **push**, so the default workflow catches style and test regressions before they reach a shared branch. The **75%** line coverage floor on `app/` is enforced in `pytest.ini` so the minimum bar stays visible in every test run.
