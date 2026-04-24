# Decision log

## Hexagonal (ports and adapters)

The API is split into a **domain** core, **use cases** that only talk to interfaces, and **infrastructure** on the outside. This keeps business rules in one place, allows swapping the database or email or JWT implementation, and makes unit tests easy by using in-memory fakes for repositories and ports.

## Why FastAPI

**FastAPI** was chosen for native async support, automatic OpenAPI documentation, and first-class Pydantic integration, which lines up with typed DTOs in the input ports and with fast iteration on a take-home scope. Compared to Flask it reduces boilerplate for dependencies and validation; compared to full Django, it keeps the project small and easy to keep aligned with a strict layered design.

## PostgreSQL with asyncpg and async SQLAlchemy 2.0

The database is **PostgreSQL** in production. **asyncpg** plus **SQLAlchemy 2.0** async engine/sessions let request handlers and repositories use `async/await` end to end, which matches FastAPI and avoids mixing blocking DB calls in async routes. A synchronous URL (`postgresql+psycopg`) is used for **Alembic** CLI migrations; the app runtime uses `postgresql+asyncpg`.

## Fake email adapter: sync vs async

The `IEmailPort` contract has **sync** `send_invitation_sync` (so the use case can return a `NotificationResult` in the same response) and **async** `send_invitation_async` (logging only, no return). The “fake” adapter prints for sync and uses the `logging` module for async, matching the challenge: simulate notification without a real mail server, while still demonstrating both code paths.

## JWT with python-jose

**python-jose** is used to issue and verify JWTs with a configurable `SECRET_KEY`, `ALGORITHM`, and expiry, using the standard `sub` and `exp` claims. It fits a small project without pulling in a larger auth stack; tokens are validated in the `get_current_user` dependency and invalid/expired tokens map to 401 and domain `InvalidCredentialsException` where appropriate.

## Task status transitions

Only these transitions are allowed: **pending** → **in_progress**; **in_progress** → **done**; **in_progress** → **pending**. This gives a small state machine: work cannot jump from pending to done without “starting,” and “done” is a terminal state from the perspective of forward progress, while **in_progress** can roll back to **pending**. Any other change raises `InvalidTaskStatusTransitionException` (exposed as HTTP 422).

## Password hashing with bcrypt

**passlib** with **bcrypt** hashes passwords on registration; login verifies with a constant-time check. A compatible **bcrypt** package version is pinned so the stack works reliably with `passlib` in CI and Docker.

## Docker and Compose

A **multistage** build installs dependencies in a builder image and copies site-packages into a small runtime image. **docker-compose** runs PostgreSQL 16, waits for it with a health check, and starts the API after `alembic upgrade head` so a fresh clone can run with no local PostgreSQL.
