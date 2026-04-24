from datetime import UTC, datetime

from app.domain.exceptions.task import (
    InvalidTaskStatusTransitionException,
    TaskNotFoundException,
)
from app.domain.exceptions.task_list import TaskListNotFoundException
from app.domain.value_objects.status import TaskStatus
from app.ports.input.task_use_cases import (
    ChangeTaskStatusInput,
    ChangeTaskStatusOutput,
    IChangeTaskStatus,
)
from app.ports.output.task_list_repository import ITaskListRepository
from app.ports.output.task_repository import ITaskRepository

from app.application.task._mappers import task_to_out


_VALID_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.PENDING: {TaskStatus.IN_PROGRESS},
    TaskStatus.IN_PROGRESS: {TaskStatus.DONE, TaskStatus.PENDING},
    TaskStatus.DONE: set(),
}


class ChangeTaskStatus(IChangeTaskStatus):
    def __init__(
        self,
        task_repository: ITaskRepository,
        task_list_repository: ITaskListRepository,
    ) -> None:
        self._task_repository = task_repository
        self._task_list_repository = task_list_repository

    @staticmethod
    def _assert_transition(
        current: TaskStatus, new: TaskStatus
    ) -> None:
        allowed = _VALID_TRANSITIONS.get(current, set())
        if new not in allowed:
            raise InvalidTaskStatusTransitionException(
                f"Cannot transition from {current.value} to {new.value}"
            )

    async def execute(
        self, data: ChangeTaskStatusInput
    ) -> ChangeTaskStatusOutput:
        task_list = await self._task_list_repository.find_by_id(
            data.task_list_id
        )
        if task_list.owner_id != data.requester_id:
            raise TaskListNotFoundException("Task list not found")
        task = await self._task_repository.find_by_id(data.task_id)
        if task.task_list_id != data.task_list_id:
            raise TaskNotFoundException("Task not found")
        self._assert_transition(task.status, data.new_status)
        task.status = data.new_status
        task.updated_at = datetime.now(UTC)
        updated = await self._task_repository.update(task)
        return ChangeTaskStatusOutput(task=task_to_out(updated, None))
