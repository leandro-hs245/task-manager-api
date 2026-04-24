from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from app.domain.entities.task import Task
from app.domain.entities.task_list import TaskList
from app.domain.entities.user import User
from app.domain.exceptions.task import TaskNotFoundException
from app.domain.exceptions.task_list import TaskListNotFoundException
from app.domain.exceptions.user import UserNotFoundException
from app.domain.value_objects.priority import TaskPriority
from app.domain.value_objects.status import TaskStatus
from app.ports.output.auth_port import IAuthPort
from app.ports.output.email_port import IEmailPort, NotificationResult
from app.ports.output.task_list_repository import ITaskListRepository
from app.ports.output.task_repository import ITaskRepository
from app.ports.output.user_repository import IUserRepository


@dataclass
class InMemoryUserRepository(IUserRepository):
    _by_id: dict[UUID, User] = field(default_factory=dict)
    _by_email: dict[str, UUID] = field(default_factory=dict)

    async def save(self, user: User) -> User:
        self._by_id[user.id] = user
        self._by_email[user.email] = user.id
        return user

    async def find_by_id(self, user_id: UUID) -> User:
        u = self._by_id.get(user_id)
        if u is None:
            raise UserNotFoundException("User not found")
        return u

    async def find_by_email(self, email: str) -> User:
        uid = self._by_email.get(email)
        if uid is None:
            raise UserNotFoundException("User not found")
        return self._by_id[uid]

    async def update(self, user: User) -> User:
        if user.id not in self._by_id:
            raise UserNotFoundException("User not found")
        self._by_id[user.id] = user
        self._by_email[user.email] = user.id
        return user

    async def delete(self, user_id: UUID) -> None:
        u = self._by_id.pop(user_id, None)
        if u is None:
            raise UserNotFoundException("User not found")
        for k, v in list(self._by_email.items()):
            if v == user_id:
                del self._by_email[k]
                break


@dataclass
class InMemoryTaskListRepository(ITaskListRepository):
    _rows: dict[UUID, TaskList] = field(default_factory=dict)

    async def save(self, task_list: TaskList) -> TaskList:
        self._rows[task_list.id] = task_list
        return task_list

    async def find_by_id(self, task_list_id: UUID) -> TaskList:
        r = self._rows.get(task_list_id)
        if r is None:
            raise TaskListNotFoundException("Not found")
        return r

    async def find_all_by_owner(self, owner_id: UUID) -> list[TaskList]:
        return [t for t in self._rows.values() if t.owner_id == owner_id]

    async def update(self, task_list: TaskList) -> TaskList:
        if task_list.id not in self._rows:
            raise TaskListNotFoundException("Not found")
        self._rows[task_list.id] = task_list
        return task_list

    async def delete(self, task_list_id: UUID) -> None:
        if task_list_id not in self._rows:
            raise TaskListNotFoundException("Not found")
        del self._rows[task_list_id]


@dataclass
class InMemoryTaskRepository(ITaskRepository):
    _rows: dict[UUID, Task] = field(default_factory=dict)

    async def save(self, task: Task) -> Task:
        self._rows[task.id] = task
        return task

    async def find_by_id(self, task_id: UUID) -> Task:
        t = self._rows.get(task_id)
        if t is None:
            raise TaskNotFoundException("not found")
        return t

    async def find_all_by_list_id(
        self,
        task_list_id: UUID,
        status: TaskStatus | None,
        priority: TaskPriority | None,
    ) -> list[Task]:
        res = [t for t in self._rows.values() if t.task_list_id == task_list_id]
        if status is not None:
            res = [t for t in res if t.status == status]
        if priority is not None:
            res = [t for t in res if t.priority == priority]
        return res

    async def update(self, task: Task) -> Task:
        if task.id not in self._rows:
            raise TaskNotFoundException("not found")
        self._rows[task.id] = task
        return task

    async def delete(self, task_id: UUID) -> None:
        if task_id not in self._rows:
            raise TaskNotFoundException("not found")
        del self._rows[task_id]


class _FakeAuth(IAuthPort):
    def __init__(self) -> None:
        self._t: dict[str, UUID] = {}

    def create_token(self, user_id: UUID) -> str:
        tok = f"tok_{user_id!s}"
        self._t[tok] = user_id
        return tok

    def verify_token(self, token: str) -> UUID:
        u = self._t.get(token)
        if u is None:
            from app.domain.exceptions.user import InvalidCredentialsException

            raise InvalidCredentialsException("bad")
        return u


class _FakeEmail(IEmailPort):
    def send_invitation_sync(
        self, to_email: str, task_title: str, assigned_by: str
    ) -> NotificationResult:
        return NotificationResult(
            to=to_email,
            subject=task_title,
            status="sent",
        )

    def send_invitation_async(
        self, to_email: str, task_title: str, assigned_by: str
    ) -> None:
        return None
