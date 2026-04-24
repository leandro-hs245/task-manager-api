Backend Technical Challenge

Congratulations on reaching this stage!
We would like to thank you for the time you have dedicated to our selection process. We know that each stage requires effort, and we value the commitment you are putting into each one. Now, the time has come to demonstrate your knowledge and experience by solving this case.
This challenge aims to evaluate:

    REST API Design and clean code structure.

    Use of modern development tools in Python.

    Technical thinking and the ability to justify decisions.

    Best practices: Testing, Docker, linters, and validations.

    Estimated time: 4-6 hours. If you cannot cover everything, prioritize the core functionality and document what remains pending.

About the Challenge

Requirements:

    Language: Python

    API Framework: FastAPI

    Database: Implement a real database of your choice.

    Testing: pytest or unittest

    Linter: flake8 or pylint

    Code Formatting: black

    Docker: Configuration of a Docker container to run the application.

Details
1. Use Cases

a. Basic Use Cases:

    Create, retrieve, update, and delete task lists.

    Create, retrieve, update, and delete tasks within a list.

    Change the status of a task.

    List all tasks from a list with filters by status or priority, including an extra field indicating the completion percentage.

b. Bonus Use Cases (Optional):

    Login and Authentication: Optional implementation of JWT to protect endpoints.

    Task Assignment: Assign a responsible user to each task.

    Mock Notification: Simulation of sending an invitation to users via email (not a real email).

2. Project Structure

    Clean Architecture by layers (Domain, Application/UseCases, Infrastructure).

    Strong typing with Pydantic.

    Error handling with custom exceptions.

    Business logic validations.

    Unit and integration testing with pytest.

    Linters (flake8, ruff) and formatting (black, isort).

    Dockerfile (multi-stage if applicable) and docker-compose.

    Comprehensive README + a DECISION_LOG.md file explaining technical decisions.

3. Testing

    Implement unit and integration tests using pytest.

    Tests must cover 75% of the project.

    Include a pytest.ini file for configuration.

4. Linter and Code Formatting

    Configure flake8 as the project linter.

    Configure black as the code formatter.

    Include a .flake8 file with specific configurations (e.g., ignoring certain rules).

5. Docker

    Provide a Dockerfile to create the Docker image for the application.

    Include an optional docker-compose.yml file to facilitate running the application.

6. README

The README.md file must include:

    Project description.

    Instructions for local environment setup.

    Instructions for running the application in Docker.

    Instructions for running the tests.

Upon completion, remember to send your repository as a reply to the email.

Good luck!


# Requirements & Prompts:


## Phase 1 — Domain Layer

### Prompt 1.1 — Value Objects
This project uses hexagonal architecture with FastAPI, PostgreSQL (asyncpg),
Python 3.12, and JWT authentication.

In app/domain/value_objects/ create:
- status.py: TaskStatus enum (pending, in_progress, done)
- priority.py: TaskPriority enum (low, medium, high)

These are pure Python enums with no external dependencies.

### Prompt 1.2 — Entities
In app/domain/entities/ create the following pure Python dataclasses.
No SQLAlchemy, FastAPI, or Pydantic imports allowed here.

- user.py: User with fields:
  id (UUID), email (str), full_name (str), hashed_password (str), created_at (datetime)

- task_list.py: TaskList with fields:
  id (UUID), name (str), description (str | None), owner_id (UUID),
  created_at (datetime), updated_at (datetime)

- task.py: Task with fields:
  id (UUID), title (str), description (str | None), status (TaskStatus),
  priority (TaskPriority), task_list_id (UUID), assigned_user_id (UUID | None),
  created_at (datetime), updated_at (datetime)

Import TaskStatus and TaskPriority from app.domain.value_objects.
Use Python 3.12 strong typing throughout.

### Prompt 1.3 — Domain Exceptions
In app/domain/exceptions/ create:
- base.py: BaseDomainException(Exception) as the root exception class,
  with a message field.

- task.py:
  TaskNotFoundException(BaseDomainException)
  TaskAlreadyExistsException(BaseDomainException)
  InvalidTaskStatusTransitionException(BaseDomainException)

- task_list.py:
  TaskListNotFoundException(BaseDomainException)
  TaskListAlreadyExistsException(BaseDomainException)

- user.py:
  UserNotFoundException(BaseDomainException)
  UserAlreadyExistsException(BaseDomainException)
  InvalidCredentialsException(BaseDomainException)

All exceptions inherit from BaseDomainException.


## Phase 2 — Ports

### Prompt 2.1 — Output Ports
In app/ports/output/ create abstract interfaces using Python ABC.
No implementation, only contracts. Use Python 3.12 typing throughout.

- task_repository.py: ITaskRepository
  - save(task: Task) -> Task
  - find_by_id(task_id: UUID) -> Task
  - find_all_by_list_id(task_list_id: UUID, status: TaskStatus | None, priority: TaskPriority | None) -> list[Task]
  - update(task: Task) -> Task
  - delete(task_id: UUID) -> None

- task_list_repository.py: ITaskListRepository
  - save(task_list: TaskList) -> TaskList
  - find_by_id(task_list_id: UUID) -> TaskList
  - find_all_by_owner(owner_id: UUID) -> list[TaskList]
  - update(task_list: TaskList) -> TaskList
  - delete(task_list_id: UUID) -> None

- user_repository.py: IUserRepository
  - save(user: User) -> User
  - find_by_id(user_id: UUID) -> User
  - find_by_email(email: str) -> User
  - update(user: User) -> User
  - delete(user_id: UUID) -> None

- email_port.py: IEmailPort
  - send_invitation_sync(to_email: str, task_title: str, assigned_by: str) -> NotificationResult
  - send_invitation_async(to_email: str, task_title: str, assigned_by: str) -> None
  Also define NotificationResult as a dataclass with fields: to (str), subject (str), status (str)

- auth_port.py: IAuthPort
  - create_token(user_id: UUID) -> str
  - verify_token(token: str) -> UUID

### Prompt 2.2 — Input Ports
In app/ports/input/ create use case interfaces using Python ABC.
Define Pydantic BaseModel DTOs in the same file as each interface.
Each interface must define an execute() method with typed input/output.

- task_list_use_cases.py:
  ICreateTaskList, IGetTaskList, IUpdateTaskList, IDeleteTaskList

- task_use_cases.py:
  ICreateTask, IGetTask, IUpdateTask, IDeleteTask,
  IChangeTaskStatus, IListTasksByList
  For IListTasksByList the output DTO must include completion_percentage (float)

- auth_use_cases.py:
  IRegisterUser, ILoginUser
  LoginUser output DTO must include access_token and token_type fields


## Phase 3 — Application Layer

### Prompt 3.1 — Task List Use Cases
In app/application/task_list/ implement:
- create_task_list.py: CreateTaskList implementing ICreateTaskList
- get_task_list.py: GetTaskList implementing IGetTaskList
- update_task_list.py: UpdateTaskList implementing IUpdateTaskList
- delete_task_list.py: DeleteTaskList implementing IDeleteTaskList

Rules for all use cases:
- Receive repository dependencies via __init__ constructor injection
- Use only domain entities and port interfaces, no SQLAlchemy or FastAPI imports
- Raise appropriate domain exceptions on business rule violations
- Generate UUIDs and timestamps at use case level, not at DB level

### Prompt 3.2 — Task Use Cases
In app/application/task/ implement:

- create_task.py: CreateTask implementing ICreateTask
  - If assigned_user_id is provided:
    - Fetch the assigned user from IUserRepository to get their email
    - Call email_port.send_invitation_sync() and include the NotificationResult
      in the return value (add notification field to output DTO)
  - If no assigned_user_id, notification field is None

- get_task.py: GetTask implementing IGetTask
- update_task.py: UpdateTask implementing IUpdateTask
- delete_task.py: DeleteTask implementing IDeleteTask

- change_task_status.py: ChangeTaskStatus implementing IChangeTaskStatus
  Valid transitions only:
  - pending -> in_progress
  - in_progress -> done
  - in_progress -> pending
  Raise InvalidTaskStatusTransitionException for any other transition.

- list_tasks.py: ListTasksByList implementing IListTasksByList
  - Accept optional status and priority filters
  - Calculate completion_percentage = (done tasks / total tasks) * 100
  - Return 0.0 if there are no tasks

Constructor must inject: ITaskRepository, IUserRepository, IEmailPort where needed.

### Prompt 3.3 — Auth Use Cases
In app/application/auth/ implement:

- register_user.py: RegisterUser implementing IRegisterUser
  - Check if email already exists via IUserRepository, raise UserAlreadyExistsException if so
  - Hash password using bcrypt (passlib[bcrypt])
  - Save user and return user data (no password in output)

- login_user.py: LoginUser implementing ILoginUser
  - Find user by email, raise InvalidCredentialsException if not found
  - Verify bcrypt password hash, raise InvalidCredentialsException if mismatch
  - Generate JWT token via IAuthPort and return it with token_type: "bearer"

Constructor injects: IUserRepository, IAuthPort


## Phase 4 — Infrastructure / Driven Adapters

### Prompt 4.1 — Database Models & Session
In app/adapters/output/db/ set up:

- session.py:
  - Async SQLAlchemy engine using asyncpg
  - Read DATABASE_URL from environment variables using python-dotenv
  - Async session factory
  - Base declarative class

- models/user.py, models/task_list.py, models/task.py:
  SQLAlchemy 2.0 ORM models using Mapped and mapped_column.
  Mirror the domain entities exactly.
  Use server_default=func.now() for timestamps.
  Define relationships between models.

- Configure Alembic in migrations/ at the project root with async support (asyncpg).
  Generate the initial migration for all three models.

Read all config from environment variables. Do not hardcode any values.
Fill the .env file with all required PostgreSQL variables:
DATABASE_URL, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT


*** After Phase 4.1 run alembic upgrade head before continuing

### Prompt 4.2 — Repository Implementations
In app/adapters/output/db/repositories/ implement:

- task_repository.py: SQLAlchemyTaskRepository implementing ITaskRepository
- task_list_repository.py: SQLAlchemyTaskListRepository implementing ITaskListRepository
- user_repository.py: SQLAlchemyUserRepository implementing IUserRepository

Each repository must:
- Receive an async SQLAlchemy session via constructor injection
- Map between ORM models and domain entities in both directions
  (from_orm and to_orm mapper methods)
- Use async/await for all DB operations
- Raise the appropriate domain exceptions (e.g. TaskNotFoundException)
  when records are not found instead of returning None

### Prompt 4.3 — Email Adapter
In app/adapters/output/email/ create:

- fake_email_adapter.py: FakeEmailAdapter implementing IEmailPort

  send_invitation_sync(to_email, task_title, assigned_by) -> NotificationResult:
    - Print to console: "[FAKE EMAIL] To: {to_email} | Task: '{task_title}' | Assigned by: {assigned_by}"
    - Return NotificationResult(to=to_email, subject=f"You have been assigned to '{task_title}'", status="sent")

  send_invitation_async(to_email, task_title, assigned_by) -> None:
    - Only log using Python logging module (do not print, do not return data)
    - Format: "[FAKE EMAIL - ASYNC] To: {to_email} | Task: '{task_title}' | Assigned by: {assigned_by}"

### Prompt 4.4 — JWT Adapter
In app/adapters/output/auth/ create:

- jwt_adapter.py: JWTAdapter implementing IAuthPort using python-jose[cryptography]

  create_token(user_id: UUID) -> str:
    - Create JWT with sub=str(user_id) and exp claim
    - Read SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES from environment variables

  verify_token(token: str) -> UUID:
    - Decode and validate JWT
    - Raise InvalidCredentialsException if token is invalid or expired
    - Return UUID from sub claim

Fill the .env file with: SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


## Phase 5 — API Layer

### Prompt 5.1 — Schemas & Dependencies
In app/adapters/input/api/v1/ create:

schemas/
- user.py: UserRegister, UserLogin, UserResponse, TokenResponse (with access_token, token_type)
- task_list.py: TaskListCreate, TaskListUpdate, TaskListResponse
- task.py: TaskCreate, TaskUpdate, TaskResponse, TaskStatusUpdate
  TaskResponse must include an optional notification field (NotificationResult | None)
  TaskListResponse must include completion_percentage: float

dependencies/
- db.py: get_db async dependency yielding an AsyncSession
- auth.py: get_current_user dependency
  - Extracts Bearer token from Authorization header
  - Validates via JWTAdapter
  - Fetches and returns the User entity from IUserRepository
  - Raises HTTP 401 if token is missing, invalid, or expired

### Prompt 5.2 — Routers
In app/adapters/input/api/v1/routers/ create:

- auth_router.py (prefix: /auth, no auth required):
  POST /auth/register -> 201 UserResponse
  POST /auth/login -> 200 TokenResponse

- task_list_router.py (prefix: /lists, auth required on all):
  POST /lists -> 201 TaskListResponse
  GET /lists -> 200 list[TaskListResponse]
  GET /lists/{list_id} -> 200 TaskListResponse
  PUT /lists/{list_id} -> 200 TaskListResponse
  DELETE /lists/{list_id} -> 204

- task_router.py (prefix: /lists/{list_id}/tasks, auth required on all):
  POST /lists/{list_id}/tasks -> 201 TaskResponse (includes notification if user assigned)
  GET /lists/{list_id}/tasks -> 200 list[TaskResponse]
    Query params: status (optional), priority (optional)
  GET /lists/{list_id}/tasks/{task_id} -> 200 TaskResponse
  PUT /lists/{list_id}/tasks/{task_id} -> 200 TaskResponse
  DELETE /lists/{list_id}/tasks/{task_id} -> 204
  PATCH /lists/{list_id}/tasks/{task_id}/status -> 200 TaskResponse

Wire each endpoint using dependency injection.
Use get_current_user on all protected routes.

### Prompt 5.3 — App Entry Point & Error Handlers
In app/adapters/input/api/main.py create the FastAPI app:

- Include all routers under prefix /api/v1
- Add CORSMiddleware allowing all origins (configurable via env)
- Add a startup event that verifies the DB connection

Add global exception handlers mapping domain exceptions to HTTP responses:
- TaskNotFoundException, TaskListNotFoundException, UserNotFoundException -> 404
- TaskAlreadyExistsException, TaskListAlreadyExistsException, UserAlreadyExistsException -> 409
- InvalidCredentialsException -> 401
- InvalidTaskStatusTransitionException -> 422
- BaseDomainException (catch-all) -> 400

Each error response must follow the format: { "detail": "exception message" }


## Phase 6 — Docker & Config

### Prompt 6.1 — Docker
Create:

Dockerfile (multistage, Python 3.12-slim):
- Stage 1 (builder): install all dependencies from requirements.txt
- Stage 2 (runtime): copy only app code and installed packages,
  run with: uvicorn app.adapters.input.api.main:app --host 0.0.0.0 --port 8000

docker-compose.yml with three services:
- api: builds from Dockerfile, depends_on db (with health check condition),
  loads .env file, exposes port 8000
  add a command to run alembic upgrade head before starting uvicorn
- db: postgres:16-alpine
  - uses a named volume for data persistence
  - reads POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB from .env
  - exposes port 5432
  - includes a healthcheck using pg_isready so the api waits until
    the database is actually ready before starting

Also create:
- .dockerignore: exclude env/, .venv/, __pycache__, .git, tests/, *.pyc, .env
- requirements.txt with all project dependencies pinned:
  fastapi[standard], uvicorn[standard], sqlalchemy[asyncio], asyncpg, alembic,
  pydantic, pydantic-settings, python-jose[cryptography], passlib[bcrypt],
  python-dotenv, httpx, pytest, pytest-asyncio, pytest-cov, aiosqlite, black, isort, flake8

The DATABASE_URL in .env should point to the db service by name:
postgresql+asyncpg://user:password@db:5432/dbname
so no local PostgreSQL installation is needed at all.


## Phase 7 — Tests

### Prompt 7.1 — Test Infrastructure
Set up the full test infrastructure:

pytest.ini:
- testpaths = tests
- asyncio_mode = auto
- addopts = --cov=app --cov-report=term-missing --cov-fail-under=75

tests/conftest.py — create the following fixtures:
- event_loop: override default asyncio event loop
- test_engine: async SQLite engine (aiosqlite) with all models created
- test_session: async session bound to test_engine
- fake_email_adapter: instance of FakeEmailAdapter
- fake_auth_adapter: in-memory IAuthPort that creates/verifies fake tokens
- test_client: httpx AsyncClient with FastAPI dependency overrides:
  - override get_db with test_session
  - override get_current_user with a fixed test User
- sample_user, sample_task_list, sample_task: factory fixtures
  that insert records into the test DB and return domain entities

Add aiosqlite to requirements.txt.

### Prompt 7.2 — Unit Tests
In tests/unit/ create:

- test_task_entity.py:
  Test Task creation with valid fields
  Test that TaskStatus and TaskPriority enums have expected values

- test_status_transitions.py:
  Test valid transitions: pending->in_progress, in_progress->done, in_progress->pending
  Test invalid transitions raise InvalidTaskStatusTransitionException:
  pending->done, done->pending, done->in_progress

- test_create_task.py:
  Test CreateTask use case with fake repository and fake email port
  Test notification is returned when assigned_user_id is provided
  Test notification is None when no user is assigned

- test_list_tasks.py:
  Test completion_percentage = 0.0 when no tasks
  Test completion_percentage = 100.0 when all tasks are done
  Test completion_percentage = 50.0 when half tasks are done

- test_register_user.py:
  Test successful registration
  Test UserAlreadyExistsException when email already exists

- test_login_user.py:
  Test successful login returns token
  Test InvalidCredentialsException on wrong password
  Test InvalidCredentialsException on unknown email

All tests use in-memory fake adapters, no DB or HTTP calls.

### Prompt 7.3 — Integration Tests
In tests/integration/ create:

- test_auth_endpoints.py:
  Test POST /api/v1/auth/register -> 201
  Test POST /api/v1/auth/register with duplicate email -> 409
  Test POST /api/v1/auth/login with valid credentials -> 200 with token
  Test POST /api/v1/auth/login with wrong password -> 401

- test_task_list_endpoints.py:
  Test full CRUD cycle for task lists
  Test GET /lists returns only lists owned by current user
  Test DELETE returns 204
  Test GET non-existent list returns 404

- test_task_endpoints.py:
  Test full CRUD cycle for tasks within a list
  Test GET /tasks with ?status= filter
  Test GET /tasks with ?priority= filter
  Test PATCH /tasks/{id}/status with valid transition -> 200
  Test PATCH /tasks/{id}/status with invalid transition -> 422
  Test POST task with assigned_user_id includes notification in response

- test_completion_percentage.py:
  Create a task list with 4 tasks: 2 done, 1 in_progress, 1 pending
  Call GET /lists/{id}/tasks
  Assert completion_percentage == 50.0

Each test must be fully independent. Use the fixtures from conftest.py.


## Phase 8 — Documentation

### Prompt 8.1 — README & DECISION_LOG
Create README.md including:
- Project description and full feature list
- Architecture overview explaining hexagonal architecture and how ports/adapters are used
- Prerequisites: Python 3.12, Docker, PostgreSQL
- Local setup: venv activation, pip install -r requirements.txt,
  copy .env.example to .env, alembic upgrade head, uvicorn command
- Docker setup: docker-compose up --build
- Running tests: pytest (explain coverage threshold of 75%)
- Environment variables reference table with descriptions for all vars in .env
- API endpoints summary table with method, path, auth required, and description

Create DECISION_LOG.md explaining:
- Why hexagonal architecture (swappable adapters, email port, testability)
- Why FastAPI over Flask/Django
- Why PostgreSQL with asyncpg for async performance
- Why async SQLAlchemy 2.0
- Why FakeEmailAdapter: sync returns payload in response, async only logs
- Why JWT with python-jose
- Status transition validation design and why only specific transitions are allowed
- Why bcrypt for password hashing

Don't mention this @project_overview.md file in the files, this one will be deleted manually after everything works as intended.