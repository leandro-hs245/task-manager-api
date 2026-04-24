from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.task import Task
from app.domain.value_objects.priority import TaskPriority
from app.domain.value_objects.status import TaskStatus


class ITaskRepository(ABC):
    @abstractmethod
    async def save(self, task: Task) -> Task: ...

    @abstractmethod
    async def find_by_id(self, task_id: UUID) -> Task: ...

    @abstractmethod
    async def find_all_by_list_id(
        self,
        task_list_id: UUID,
        status: TaskStatus | None,
        priority: TaskPriority | None,
    ) -> list[Task]: ...

    @abstractmethod
    async def update(self, task: Task) -> Task: ...

    @abstractmethod
    async def delete(self, task_id: UUID) -> None: ...
