from app.domain.entities.task import Task
from app.ports.input.task_use_cases import TaskOut
from app.ports.output.email_port import NotificationResult


def task_to_out(
    task: Task, notification: NotificationResult | None = None
) -> TaskOut:
    return TaskOut(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        task_list_id=task.task_list_id,
        assigned_user_id=task.assigned_user_id,
        created_at=task.created_at,
        updated_at=task.updated_at,
        notification=notification,
    )
