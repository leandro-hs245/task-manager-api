from enum import Enum


class TaskPriority(str, Enum):
    """Task priority level."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
