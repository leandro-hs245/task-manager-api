from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.value_objects.priority import TaskPriority
from app.domain.value_objects.status import TaskStatus
from app.ports.output.email_port import NotificationResult


class TaskOut(BaseModel):
    """Task fields returned from use cases (application DTO)."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    task_list_id: UUID
    assigned_user_id: UUID | None
    created_at: datetime
    updated_at: datetime
    notification: NotificationResult | None = None


class CreateTaskInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: str | None = None
    priority: TaskPriority
    task_list_id: UUID
    requester_id: UUID
    assigned_user_id: UUID | None = None
    status: TaskStatus = TaskStatus.PENDING


class CreateTaskOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task: TaskOut


class GetTaskInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: UUID
    task_list_id: UUID
    requester_id: UUID


class GetTaskOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task: TaskOut


class UpdateTaskInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: UUID
    task_list_id: UUID
    requester_id: UUID
    title: str | None = None
    description: str | None = None
    priority: TaskPriority | None = None
    assigned_user_id: UUID | None = None
    status: TaskStatus | None = None


class UpdateTaskOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task: TaskOut


class DeleteTaskInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: UUID
    task_list_id: UUID
    requester_id: UUID


class ChangeTaskStatusInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: UUID
    task_list_id: UUID
    requester_id: UUID
    new_status: TaskStatus


class ChangeTaskStatusOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task: TaskOut


class ListTasksByListInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_list_id: UUID
    requester_id: UUID
    status: TaskStatus | None = None
    priority: TaskPriority | None = None


class ListTasksByListOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tasks: list[TaskOut]
    completion_percentage: float


class ICreateTask(ABC):
    @abstractmethod
    async def execute(self, data: CreateTaskInput) -> CreateTaskOutput: ...


class IGetTask(ABC):
    @abstractmethod
    async def execute(self, data: GetTaskInput) -> GetTaskOutput: ...


class IUpdateTask(ABC):
    @abstractmethod
    async def execute(self, data: UpdateTaskInput) -> UpdateTaskOutput: ...


class IDeleteTask(ABC):
    @abstractmethod
    async def execute(self, data: DeleteTaskInput) -> None: ...


class IChangeTaskStatus(ABC):
    @abstractmethod
    async def execute(self, data: ChangeTaskStatusInput) -> ChangeTaskStatusOutput: ...


class IListTasksByList(ABC):
    @abstractmethod
    async def execute(self, data: ListTasksByListInput) -> ListTasksByListOutput: ...
