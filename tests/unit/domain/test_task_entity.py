from datetime import UTC, datetime
from uuid import uuid4

from app.domain.entities.task import Task
from app.domain.value_objects.priority import TaskPriority
from app.domain.value_objects.status import TaskStatus


def test_task_status_values() -> None:
    assert TaskStatus.PENDING.value == "pending"
    assert TaskStatus.IN_PROGRESS.value == "in_progress"
    assert TaskStatus.DONE.value == "done"


def test_task_priority_values() -> None:
    assert TaskPriority.LOW.value == "low"
    assert TaskPriority.MEDIUM.value == "medium"
    assert TaskPriority.HIGH.value == "high"


def test_task_dataclass() -> None:
    now = datetime.now(UTC)
    tid = uuid4()
    lid = uuid4()
    t = Task(
        id=tid,
        title="t",
        description="d",
        status=TaskStatus.PENDING,
        priority=TaskPriority.LOW,
        task_list_id=lid,
        assigned_user_id=None,
        created_at=now,
        updated_at=now,
    )
    assert t.title == "t"
    assert t.status is TaskStatus.PENDING
