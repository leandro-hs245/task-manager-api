from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.application.task.create_task import CreateTask
from app.domain.entities.task_list import TaskList
from app.domain.entities.user import User
from app.domain.value_objects.priority import TaskPriority
from app.domain.value_objects.status import TaskStatus
from app.ports.input.task_use_cases import CreateTaskInput
from tests.fakes import (
    InMemoryTaskListRepository,
    InMemoryTaskRepository,
    InMemoryUserRepository,
    _FakeEmail,
)


def _now() -> datetime:
    return datetime.now(UTC)


@pytest.mark.asyncio
async def test_create_with_assignee_sends_notification() -> None:
    owner = uuid4()
    assignee = uuid4()
    lid = uuid4()
    tlr = InMemoryTaskListRepository()
    tlr._rows[lid] = TaskList(
        id=lid,
        name="L",
        description=None,
        owner_id=owner,
        created_at=_now(),
        updated_at=_now(),
    )
    tr = InMemoryTaskRepository()
    ur = InMemoryUserRepository()
    now = _now()
    ur._by_id[owner] = User(
        id=owner,
        email="o@x.com",
        full_name="Owner",
        hashed_password="x",
        created_at=now,
    )
    ur._by_email["o@x.com"] = owner
    ur._by_id[assignee] = User(
        id=assignee,
        email="a@x.com",
        full_name="A",
        hashed_password="x",
        created_at=now,
    )
    ur._by_email["a@x.com"] = assignee
    em = _FakeEmail()
    uc = CreateTask(tr, tlr, ur, em)
    out = await uc.execute(
        CreateTaskInput(
            title="t",
            description=None,
            priority=TaskPriority.LOW,
            task_list_id=lid,
            requester_id=owner,
            assigned_user_id=assignee,
            status=TaskStatus.PENDING,
        )
    )
    assert out.task.notification is not None
    assert out.task.notification.to == "a@x.com"


@pytest.mark.asyncio
async def test_create_without_assignee_no_notification() -> None:
    owner = uuid4()
    lid = uuid4()
    tlr = InMemoryTaskListRepository()
    tlr._rows[lid] = TaskList(
        id=lid,
        name="L",
        description=None,
        owner_id=owner,
        created_at=_now(),
        updated_at=_now(),
    )
    tr = InMemoryTaskRepository()
    ur = InMemoryUserRepository()
    now = _now()
    ur._by_id[owner] = User(
        id=owner,
        email="o@x.com",
        full_name="Owner",
        hashed_password="x",
        created_at=now,
    )
    ur._by_email["o@x.com"] = owner
    uc = CreateTask(tr, tlr, ur, _FakeEmail())
    out = await uc.execute(
        CreateTaskInput(
            title="t",
            description=None,
            priority=TaskPriority.LOW,
            task_list_id=lid,
            requester_id=owner,
            assigned_user_id=None,
            status=TaskStatus.PENDING,
        )
    )
    assert out.task.notification is None
