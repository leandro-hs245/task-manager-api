import os
from contextlib import asynccontextmanager
from logging.config import dictConfig

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.adapters.input.api.v1.routers import (
    auth_router,
    task_list_router,
    task_router,
)
from app.adapters.output.db.session import get_engine
from app.domain.exceptions.base import BaseDomainException
from app.domain.exceptions.task import (
    InvalidTaskStatusTransitionException,
    TaskAlreadyExistsException,
    TaskNotFoundException,
)
from app.domain.exceptions.task_list import (
    TaskListAlreadyExistsException,
    TaskListNotFoundException,
)
from app.domain.exceptions.user import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
)

dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        },
    }
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    engine = get_engine()
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        raise RuntimeError("Database is not reachable") from e
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Task Manager API",
        lifespan=lifespan,
    )

    cors_raw = os.environ.get("CORS_ALLOW_ORIGINS", "*")
    origins = ["*"] if cors_raw == "*" else [o.strip() for o in cors_raw.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(TaskNotFoundException)
    def _not_found_t(_: Request, exc: TaskNotFoundException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message},
        )

    @app.exception_handler(TaskListNotFoundException)
    def _not_found_list(
        _: Request, exc: TaskListNotFoundException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message},
        )

    @app.exception_handler(UserNotFoundException)
    def _not_found_user(_: Request, exc: UserNotFoundException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message},
        )

    @app.exception_handler(TaskAlreadyExistsException)
    def _conflict_t(_: Request, exc: TaskAlreadyExistsException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": exc.message},
        )

    @app.exception_handler(TaskListAlreadyExistsException)
    def _conflict_l(_: Request, exc: TaskListAlreadyExistsException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": exc.message},
        )

    @app.exception_handler(UserAlreadyExistsException)
    def _conflict_user(
        _: Request, exc: UserAlreadyExistsException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": exc.message},
        )

    @app.exception_handler(InvalidCredentialsException)
    def _auth(_: Request, exc: InvalidCredentialsException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": exc.message},
        )

    @app.exception_handler(InvalidTaskStatusTransitionException)
    def _trans(_: Request, exc: InvalidTaskStatusTransitionException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.message},
        )

    @app.exception_handler(BaseDomainException)
    def _base(_: Request, exc: BaseDomainException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message},
        )

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(task_list_router, prefix="/api/v1")
    app.include_router(task_router, prefix="/api/v1")

    return app


app = create_app()
