from app.domain.value_objects.status import TaskStatus
from app.domain.exceptions.task_list import TaskListNotFoundException
from app.ports.input.task_use_cases import (
    IListTasksByList,
    ListTasksByListInput,
    ListTasksByListOutput,
)
from app.ports.output.task_list_repository import ITaskListRepository
from app.ports.output.task_repository import ITaskRepository

from app.application.task._mappers import task_to_out


class ListTasksByList(IListTasksByList):
    def __init__(
        self,
        task_repository: ITaskRepository,
        task_list_repository: ITaskListRepository,
    ) -> None:
        self._task_repository = task_repository
        self._task_list_repository = task_list_repository

    @staticmethod
    def _completion_percentage(tasks) -> float:
        total = len(tasks)
        if total == 0:
            return 0.0
        done = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        return (done / total) * 100.0

    async def execute(
        self, data: ListTasksByListInput
    ) -> ListTasksByListOutput:
        task_list = await self._task_list_repository.find_by_id(
            data.task_list_id
        )
        if task_list.owner_id != data.requester_id:
            raise TaskListNotFoundException("Task list not found")
        all_for_list = await self._task_repository.find_all_by_list_id(
            data.task_list_id, None, None
        )
        completion = self._completion_percentage(all_for_list)
        filtered = await self._task_repository.find_all_by_list_id(
            data.task_list_id, data.status, data.priority
        )
        return ListTasksByListOutput(
            tasks=[task_to_out(t, None) for t in filtered],
            completion_percentage=completion,
        )
