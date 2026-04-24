from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.task_list import TaskList


class ITaskListRepository(ABC):
    @abstractmethod
    async def save(self, task_list: TaskList) -> TaskList: ...

    @abstractmethod
    async def find_by_id(self, task_list_id: UUID) -> TaskList: ...

    @abstractmethod
    async def find_all_by_owner(self, owner_id: UUID) -> list[TaskList]: ...

    @abstractmethod
    async def update(self, task_list: TaskList) -> TaskList: ...

    @abstractmethod
    async def delete(self, task_list_id: UUID) -> None: ...
