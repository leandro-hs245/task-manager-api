from app.adapters.input.api.v1.routers.auth_router import router as auth_router
from app.adapters.input.api.v1.routers.task_list_router import (
    router as task_list_router,
)
from app.adapters.input.api.v1.routers.task_router import router as task_router

__all__ = ("auth_router", "task_list_router", "task_router")
