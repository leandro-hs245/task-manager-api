from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from app.application.task.change_task_status import ChangeTaskStatus
from app.domain.entities.task import Task
from app.domain.entities.task_list import TaskList
from app.domain.exceptions.task import InvalidTaskStatusTransitionException
from app.domain.value_objects.priority import TaskPriority
from app.domain.value_objects.status import TaskStatus
from app.ports.input.task_use_cases import ChangeTaskStatusInput
from tests.fakes import InMemoryTaskListRepository, InMemoryTaskRepository


def _now() -> datetime:
    return datetime.now(UTC)


def _make_list(owner: UUID, lid: UUID) -> TaskList:
    n = _now()
    return TaskList(
        id=lid, name="n", description=None, owner_id=owner, created_at=n, updated_at=n
    )


@pytest.mark.asyncio
async def test_valid_transitions() -> None:
    owner = uuid4()
    lid = uuid4()
    tid = uuid4()
    tlr = InMemoryTaskListRepository()
    tlr._rows[lid] = _make_list(owner, lid)
    tr = InMemoryTaskRepository()
    now = _now()
    t = Task(
        id=tid,
        title="a",
        description=None,
        status=TaskStatus.PENDING,
        priority=TaskPriority.LOW,
        task_list_id=lid,
        assigned_user_id=None,
        created_at=now,
        updated_at=now,
    )
    tr._rows[tid] = t
    uc = ChangeTaskStatus(tr, tlr)
    out = await uc.execute(
        ChangeTaskStatusInput(
            task_id=tid,
            task_list_id=lid,
            requester_id=owner,
            new_status=TaskStatus.IN_PROGRESS,
        )
    )
    assert out.task.status == TaskStatus.IN_PROGRESS
    out2 = await uc.execute(
        ChangeTaskStatusInput(
            task_id=tid,
            task_list_id=lid,
            requester_id=owner,
            new_status=TaskStatus.DONE,
        )
    )
    assert out2.task.status == TaskStatus.DONE


@pytest.mark.asyncio
async def test_invalid_pending_to_done() -> None:
    owner = uuid4()
    lid = uuid4()
    tid = uuid4()
    tlr = InMemoryTaskListRepository()
    tlr._rows[lid] = _make_list(owner, lid)
    tr = InMemoryTaskRepository()
    now = _now()
    t = Task(
        id=tid,
        title="a",
        description=None,
        status=TaskStatus.PENDING,
        priority=TaskPriority.LOW,
        task_list_id=lid,
        assigned_user_id=None,
        created_at=now,
        updated_at=now,
    )
    tr._rows[tid] = t
    uc = ChangeTaskStatus(tr, tlr)
    with pytest.raises(InvalidTaskStatusTransitionException):
        await uc.execute(
            ChangeTaskStatusInput(
                task_id=tid,
                task_list_id=lid,
                requester_id=owner,
                new_status=TaskStatus.DONE,
            )
        )
