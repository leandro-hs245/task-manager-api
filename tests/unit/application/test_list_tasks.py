from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.application.task.list_tasks import ListTasksByList
from app.domain.entities.task import Task
from app.domain.entities.task_list import TaskList
from app.domain.value_objects.priority import TaskPriority
from app.domain.value_objects.status import TaskStatus
from app.ports.input.task_use_cases import ListTasksByListInput
from tests.fakes import InMemoryTaskListRepository, InMemoryTaskRepository


def _now() -> datetime:
    return datetime.now(UTC)


@pytest.mark.asyncio
async def test_completion_zero_when_no_tasks() -> None:
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
    uc = ListTasksByList(tr, tlr)
    out = await uc.execute(
        ListTasksByListInput(
            task_list_id=lid, requester_id=owner, status=None, priority=None
        )
    )
    assert out.tasks == []
    assert out.completion_percentage == 0.0


@pytest.mark.asyncio
async def test_completion_all_done() -> None:
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
    n = _now()
    t1 = uuid4()
    t2 = uuid4()
    tr._rows[t1] = Task(
        id=t1,
        title="a",
        description=None,
        status=TaskStatus.DONE,
        priority=TaskPriority.LOW,
        task_list_id=lid,
        assigned_user_id=None,
        created_at=n,
        updated_at=n,
    )
    tr._rows[t2] = Task(
        id=t2,
        title="b",
        description=None,
        status=TaskStatus.DONE,
        priority=TaskPriority.LOW,
        task_list_id=lid,
        assigned_user_id=None,
        created_at=n,
        updated_at=n,
    )
    uc = ListTasksByList(tr, tlr)
    out = await uc.execute(
        ListTasksByListInput(
            task_list_id=lid, requester_id=owner, status=None, priority=None
        )
    )
    assert out.completion_percentage == 100.0


@pytest.mark.asyncio
async def test_completion_half() -> None:
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
    n = _now()
    t1, t2 = uuid4(), uuid4()
    tr._rows[t1] = Task(
        id=t1,
        title="a",
        description=None,
        status=TaskStatus.DONE,
        priority=TaskPriority.LOW,
        task_list_id=lid,
        assigned_user_id=None,
        created_at=n,
        updated_at=n,
    )
    tr._rows[t2] = Task(
        id=t2,
        title="b",
        description=None,
        status=TaskStatus.PENDING,
        priority=TaskPriority.LOW,
        task_list_id=lid,
        assigned_user_id=None,
        created_at=n,
        updated_at=n,
    )
    uc = ListTasksByList(tr, tlr)
    out = await uc.execute(
        ListTasksByListInput(
            task_list_id=lid, requester_id=owner, status=None, priority=None
        )
    )
    assert out.completion_percentage == 50.0
