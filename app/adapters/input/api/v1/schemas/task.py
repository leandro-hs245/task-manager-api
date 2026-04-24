from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.value_objects.priority import TaskPriority
from app.domain.value_objects.status import TaskStatus


class NotificationResultSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    to: str
    subject: str
    status: str


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    priority: TaskPriority
    assigned_user_id: UUID | None = None
    status: TaskStatus = TaskStatus.PENDING


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    priority: TaskPriority | None = None
    assigned_user_id: UUID | None = None
    status: TaskStatus | None = None


class TaskStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    new_status: TaskStatus


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    task_list_id: UUID
    assigned_user_id: UUID | None
    created_at: datetime
    updated_at: datetime
    notification: NotificationResultSchema | None = None


class ListTasksInListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tasks: list[TaskResponse]
    completion_percentage: float
