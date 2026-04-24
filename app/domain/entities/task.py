from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.value_objects.priority import TaskPriority
from app.domain.value_objects.status import TaskStatus


@dataclass
class Task:
    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    task_list_id: UUID
    assigned_user_id: UUID | None
    created_at: datetime
    updated_at: datetime
