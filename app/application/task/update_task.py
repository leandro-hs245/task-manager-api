from datetime import UTC, datetime

from app.domain.exceptions.task import TaskNotFoundException
from app.domain.exceptions.task_list import TaskListNotFoundException
from app.ports.input.task_use_cases import (
    IUpdateTask,
    UpdateTaskInput,
    UpdateTaskOutput,
)
from app.ports.output.task_list_repository import ITaskListRepository
from app.ports.output.task_repository import ITaskRepository

from app.application.task._mappers import task_to_out


class UpdateTask(IUpdateTask):
    def __init__(
        self,
        task_repository: ITaskRepository,
        task_list_repository: ITaskListRepository,
    ) -> None:
        self._task_repository = task_repository
        self._task_list_repository = task_list_repository

    async def execute(self, data: UpdateTaskInput) -> UpdateTaskOutput:
        task_list = await self._task_list_repository.find_by_id(data.task_list_id)
        if task_list.owner_id != data.requester_id:
            raise TaskListNotFoundException("Task list not found")
        task = await self._task_repository.find_by_id(data.task_id)
        if task.task_list_id != data.task_list_id:
            raise TaskNotFoundException("Task not found")
        now = datetime.now(UTC)
        if data.title is not None:
            task.title = data.title
        if data.description is not None:
            task.description = data.description
        if data.priority is not None:
            task.priority = data.priority
        if data.assigned_user_id is not None:
            task.assigned_user_id = data.assigned_user_id
        if data.status is not None:
            task.status = data.status
        task.updated_at = now
        updated = await self._task_repository.update(task)
        return UpdateTaskOutput(task=task_to_out(updated, None))
