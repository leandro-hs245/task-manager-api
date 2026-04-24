from datetime import UTC, datetime
from uuid import uuid4

from app.domain.entities.task_list import TaskList
from app.ports.input.task_list_use_cases import (
    CreateTaskListInput,
    CreateTaskListOutput,
    ICreateTaskList,
)
from app.ports.output.task_list_repository import ITaskListRepository


class CreateTaskList(ICreateTaskList):
    def __init__(self, task_list_repository: ITaskListRepository) -> None:
        self._task_list_repository = task_list_repository

    async def execute(self, data: CreateTaskListInput) -> CreateTaskListOutput:
        now = datetime.now(UTC)
        task_list = TaskList(
            id=uuid4(),
            name=data.name,
            description=data.description,
            owner_id=data.owner_id,
            created_at=now,
            updated_at=now,
        )
        saved = await self._task_list_repository.save(task_list)
        return CreateTaskListOutput(
            id=saved.id,
            name=saved.name,
            description=saved.description,
            owner_id=saved.owner_id,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
            completion_percentage=0.0,
        )
