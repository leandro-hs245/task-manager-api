from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateTaskListInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str | None = None
    owner_id: UUID


class CreateTaskListOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    name: str
    description: str | None
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    completion_percentage: float = 0.0


class GetTaskListInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_list_id: UUID
    requester_id: UUID


class GetTaskListOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    name: str
    description: str | None
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    completion_percentage: float


class UpdateTaskListInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_list_id: UUID
    requester_id: UUID
    name: str | None = None
    description: str | None = None


class UpdateTaskListOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    name: str
    description: str | None
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    completion_percentage: float


class DeleteTaskListInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_list_id: UUID
    requester_id: UUID


class ICreateTaskList(ABC):
    @abstractmethod
    async def execute(self, data: CreateTaskListInput) -> CreateTaskListOutput: ...


class IGetTaskList(ABC):
    @abstractmethod
    async def execute(self, data: GetTaskListInput) -> GetTaskListOutput: ...


class IUpdateTaskList(ABC):
    @abstractmethod
    async def execute(self, data: UpdateTaskListInput) -> UpdateTaskListOutput: ...


class IDeleteTaskList(ABC):
    @abstractmethod
    async def execute(self, data: DeleteTaskListInput) -> None: ...
