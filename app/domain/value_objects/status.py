from enum import Enum


class TaskStatus(str, Enum):
    """Task lifecycle state."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
