from app.domain.exceptions.task import TaskNotFoundException
from app.domain.exceptions.task_list import TaskListNotFoundException
from app.ports.input.task_use_cases import GetTaskInput, GetTaskOutput, IGetTask
from app.ports.output.task_list_repository import ITaskListRepository
from app.ports.output.task_repository import ITaskRepository

from app.application.task._mappers import task_to_out


class GetTask(IGetTask):
    def __init__(
        self,
        task_repository: ITaskRepository,
        task_list_repository: ITaskListRepository,
    ) -> None:
        self._task_repository = task_repository
        self._task_list_repository = task_list_repository

    async def execute(self, data: GetTaskInput) -> GetTaskOutput:
        task_list = await self._task_list_repository.find_by_id(data.task_list_id)
        if task_list.owner_id != data.requester_id:
            raise TaskListNotFoundException("Task list not found")
        task = await self._task_repository.find_by_id(data.task_id)
        if task.task_list_id != data.task_list_id:
            raise TaskNotFoundException("Task not found")
        return GetTaskOutput(task=task_to_out(task, None))
