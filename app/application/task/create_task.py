from datetime import UTC, datetime
from uuid import uuid4

from app.domain.entities.task import Task
from app.domain.exceptions.task_list import TaskListNotFoundException
from app.domain.exceptions.user import UserNotFoundException
from app.ports.input.task_use_cases import (
    CreateTaskInput,
    CreateTaskOutput,
    ICreateTask,
)
from app.ports.output.email_port import IEmailPort
from app.ports.output.task_list_repository import ITaskListRepository
from app.ports.output.task_repository import ITaskRepository
from app.ports.output.user_repository import IUserRepository

from app.application.task._mappers import task_to_out


class CreateTask(ICreateTask):
    def __init__(
        self,
        task_repository: ITaskRepository,
        task_list_repository: ITaskListRepository,
        user_repository: IUserRepository,
        email_port: IEmailPort,
    ) -> None:
        self._task_repository = task_repository
        self._task_list_repository = task_list_repository
        self._user_repository = user_repository
        self._email_port = email_port

    async def execute(self, data: CreateTaskInput) -> CreateTaskOutput:
        task_list = await self._task_list_repository.find_by_id(data.task_list_id)
        if task_list.owner_id != data.requester_id:
            raise TaskListNotFoundException("Task list not found")
        now = datetime.now(UTC)
        task = Task(
            id=uuid4(),
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            task_list_id=data.task_list_id,
            assigned_user_id=data.assigned_user_id,
            created_at=now,
            updated_at=now,
        )
        saved = await self._task_repository.save(task)
        notification = None
        if data.assigned_user_id is not None:
            try:
                assignee = await self._user_repository.find_by_id(
                    data.assigned_user_id
                )
            except UserNotFoundException as e:
                raise UserNotFoundException("Assigned user not found") from e
            try:
                requester = await self._user_repository.find_by_id(
                    data.requester_id
                )
            except UserNotFoundException as e:
                raise UserNotFoundException("Requester not found") from e
            notification = self._email_port.send_invitation_sync(
                to_email=assignee.email,
                task_title=saved.title,
                assigned_by=requester.full_name,
            )
        return CreateTaskOutput(task=task_to_out(saved, notification))
