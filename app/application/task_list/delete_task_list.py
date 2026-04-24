from app.domain.exceptions.task_list import TaskListNotFoundException
from app.ports.input.task_list_use_cases import (
    DeleteTaskListInput,
    IDeleteTaskList,
)
from app.ports.output.task_list_repository import ITaskListRepository


class DeleteTaskList(IDeleteTaskList):
    def __init__(self, task_list_repository: ITaskListRepository) -> None:
        self._task_list_repository = task_list_repository

    def _require_owner(self, list_owner_id, requester_id) -> None:
        if list_owner_id != requester_id:
            raise TaskListNotFoundException("Task list not found")

    async def execute(self, data: DeleteTaskListInput) -> None:
        tl = await self._task_list_repository.find_by_id(data.task_list_id)
        self._require_owner(tl.owner_id, data.requester_id)
        await self._task_list_repository.delete(data.task_list_id)
