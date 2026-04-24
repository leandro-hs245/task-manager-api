from app.domain.exceptions.task_list import TaskListNotFoundException
from app.domain.value_objects.status import TaskStatus
from app.ports.input.task_list_use_cases import (
    GetTaskListInput,
    GetTaskListOutput,
    IGetTaskList,
)
from app.ports.output.task_list_repository import ITaskListRepository
from app.ports.output.task_repository import ITaskRepository


class GetTaskList(IGetTaskList):
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
        total = len(tasks)
        if total == 0:
            return 0.0
        done = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        return (done / total) * 100.0

    async def execute(self, data: GetTaskListInput) -> GetTaskListOutput:
        tl = await self._task_list_repository.find_by_id(data.task_list_id)
        self._require_owner(tl.owner_id, data.requester_id)
        all_tasks = await self._task_repository.find_all_by_list_id(tl.id, None, None)
        pct = self._completion_percentage(all_tasks)
        return GetTaskListOutput(
            id=tl.id,
            name=tl.name,
            description=tl.description,
            owner_id=tl.owner_id,
            created_at=tl.created_at,
            updated_at=tl.updated_at,
            completion_percentage=pct,
        )
