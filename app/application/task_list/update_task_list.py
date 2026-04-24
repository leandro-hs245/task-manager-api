from datetime import UTC, datetime

from app.domain.exceptions.task_list import TaskListNotFoundException
from app.ports.input.task_list_use_cases import (
    IUpdateTaskList,
    UpdateTaskListInput,
    UpdateTaskListOutput,
)
from app.ports.output.task_list_repository import ITaskListRepository
from app.ports.output.task_repository import ITaskRepository


class UpdateTaskList(IUpdateTaskList):
    def __init__(
        self,
        task_list_repository: ITaskListRepository,
        task_repository: ITaskRepository,
    ) -> None:
        self._task_list_repository = task_list_repository
        self._task_repository = task_repository

    def _require_owner(self, list_owner_id, requester_id) -> None:
        if list_owner_id != requester_id:
            raise TaskListNotFoundException("Task list not found")

    @staticmethod
    def _completion_percentage(tasks) -> float:
        from app.domain.value_objects.status import TaskStatus

        total = len(tasks)
        if total == 0:
            return 0.0
        done = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        return (done / total) * 100.0

    async def execute(self, data: UpdateTaskListInput) -> UpdateTaskListOutput:
        tl = await self._task_list_repository.find_by_id(data.task_list_id)
        self._require_owner(tl.owner_id, data.requester_id)
        now = datetime.now(UTC)
        if data.name is not None:
            tl.name = data.name
        if data.description is not None:
            tl.description = data.description
        tl.updated_at = now
        updated = await self._task_list_repository.update(tl)
        all_tasks = await self._task_repository.find_all_by_list_id(
            updated.id, None, None
        )
        pct = self._completion_percentage(all_tasks)
        return UpdateTaskListOutput(
            id=updated.id,
            name=updated.name,
            description=updated.description,
            owner_id=updated.owner_id,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
            completion_percentage=pct,
        )
