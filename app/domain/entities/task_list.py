from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class TaskList:
    id: UUID
    name: str
    description: str | None
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
