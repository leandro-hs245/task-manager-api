from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.input.api.v1.dependencies.auth import get_current_user
from app.adapters.input.api.v1.schemas.task import (
    ListTasksInListResponse,
    NotificationResultSchema,
    TaskCreate,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.adapters.output.db.repositories.task_list_repository import (
    SQLAlchemyTaskListRepository,
)
from app.adapters.output.db.repositories.task_repository import SQLAlchemyTaskRepository
from app.adapters.output.db.repositories.user_repository import SQLAlchemyUserRepository
from app.adapters.output.db.session import get_db
from app.adapters.output.email.fake_email_adapter import FakeEmailAdapter
from app.application.task.change_task_status import ChangeTaskStatus
from app.application.task.create_task import CreateTask
from app.application.task.delete_task import DeleteTask
from app.application.task.get_task import GetTask
from app.application.task.list_tasks import ListTasksByList
from app.application.task.update_task import UpdateTask
from app.domain.entities.user import User
from app.domain.value_objects.priority import TaskPriority
from app.domain.value_objects.status import TaskStatus
from app.ports.input.task_use_cases import (
    ChangeTaskStatusInput,
    CreateTaskInput,
    DeleteTaskInput,
    GetTaskInput,
    ListTasksByListInput,
    TaskOut,
    UpdateTaskInput,
)

router = APIRouter(prefix="/lists/{list_id}/tasks", tags=["tasks"])


def _task_to_response(t: TaskOut) -> TaskResponse:
    notif = None
    if t.notification is not None:
        notif = NotificationResultSchema(
            to=t.notification.to,
            subject=t.notification.subject,
            status=t.notification.status,
        )
    return TaskResponse(
        id=t.id,
        title=t.title,
        description=t.description,
        status=t.status,
        priority=t.priority,
        task_list_id=t.task_list_id,
        assigned_user_id=t.assigned_user_id,
        created_at=t.created_at,
        updated_at=t.updated_at,
        notification=notif,
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    list_id: UUID,
    body: TaskCreate,
    current: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> TaskResponse:
    tr = SQLAlchemyTaskRepository(session)
    tlr = SQLAlchemyTaskListRepository(session)
    ur = SQLAlchemyUserRepository(session)
    email = FakeEmailAdapter()
    uc = CreateTask(tr, tlr, ur, email)
    out = await uc.execute(
        CreateTaskInput(
            title=body.title,
            description=body.description,
            priority=body.priority,
            task_list_id=list_id,
            requester_id=current.id,
            assigned_user_id=body.assigned_user_id,
            status=body.status,
        )
    )
    return _task_to_response(out.task)


@router.get("", response_model=ListTasksInListResponse)
async def list_tasks(
    list_id: UUID,
    current: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    status_q: TaskStatus | None = Query(
        default=None, alias="status", description="Filter by status"
    ),
    priority: TaskPriority | None = Query(
        default=None, description="Filter by priority"
    ),
) -> ListTasksInListResponse:
    tr = SQLAlchemyTaskRepository(session)
    tlr = SQLAlchemyTaskListRepository(session)
    uc = ListTasksByList(tr, tlr)
    out = await uc.execute(
        ListTasksByListInput(
            task_list_id=list_id,
            requester_id=current.id,
            status=status_q,
            priority=priority,
        )
    )
    return ListTasksInListResponse(
        tasks=[_task_to_response(t) for t in out.tasks],
        completion_percentage=out.completion_percentage,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    list_id: UUID,
    task_id: UUID,
    current: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> TaskResponse:
    uc = GetTask(
        SQLAlchemyTaskRepository(session),
        SQLAlchemyTaskListRepository(session),
    )
    o = await uc.execute(
        GetTaskInput(
            task_id=task_id,
            task_list_id=list_id,
            requester_id=current.id,
        )
    )
    return _task_to_response(o.task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    list_id: UUID,
    task_id: UUID,
    body: TaskUpdate,
    current: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> TaskResponse:
    uc = UpdateTask(
        SQLAlchemyTaskRepository(session),
        SQLAlchemyTaskListRepository(session),
    )
    o = await uc.execute(
        UpdateTaskInput(
            task_id=task_id,
            task_list_id=list_id,
            requester_id=current.id,
            title=body.title,
            description=body.description,
            priority=body.priority,
            assigned_user_id=body.assigned_user_id,
            status=body.status,
        )
    )
    return _task_to_response(o.task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_task(
    list_id: UUID,
    task_id: UUID,
    current: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Response:
    uc = DeleteTask(
        SQLAlchemyTaskRepository(session),
        SQLAlchemyTaskListRepository(session),
    )
    await uc.execute(
        DeleteTaskInput(
            task_id=task_id,
            task_list_id=list_id,
            requester_id=current.id,
        )
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{task_id}/status", response_model=TaskResponse)
async def change_status(
    list_id: UUID,
    task_id: UUID,
    body: TaskStatusUpdate,
    current: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> TaskResponse:
    uc = ChangeTaskStatus(
        SQLAlchemyTaskRepository(session),
        SQLAlchemyTaskListRepository(session),
    )
    o = await uc.execute(
        ChangeTaskStatusInput(
            task_id=task_id,
            task_list_id=list_id,
            requester_id=current.id,
            new_status=body.new_status,
        )
    )
    return _task_to_response(o.task)
