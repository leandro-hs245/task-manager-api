from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.input.api.v1.dependencies.auth import get_current_user
from app.adapters.input.api.v1.schemas.task_list import (
    TaskListCreate,
    TaskListResponse,
    TaskListUpdate,
)
from app.adapters.output.db.repositories.task_list_repository import (
    SQLAlchemyTaskListRepository,
)
from app.adapters.output.db.repositories.task_repository import SQLAlchemyTaskRepository
from app.adapters.output.db.session import get_db
from app.application.task_list.create_task_list import CreateTaskList
from app.application.task_list.delete_task_list import DeleteTaskList
from app.application.task_list.get_task_list import GetTaskList
from app.application.task_list.update_task_list import UpdateTaskList
from app.domain.entities.user import User
from app.ports.input.task_list_use_cases import (
    CreateTaskListInput,
    DeleteTaskListInput,
    GetTaskListInput,
    UpdateTaskListInput,
)

router = APIRouter(prefix="/lists", tags=["task-lists"])


@router.post("", response_model=TaskListResponse, status_code=status.HTTP_201_CREATED)
async def create_list(
    body: TaskListCreate,
    current: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> TaskListResponse:
    uc = CreateTaskList(SQLAlchemyTaskListRepository(session))
    out = await uc.execute(
        CreateTaskListInput(
            name=body.name,
            description=body.description,
            owner_id=current.id,
        )
    )
    return TaskListResponse(
        id=out.id,
        name=out.name,
        description=out.description,
        owner_id=out.owner_id,
        created_at=out.created_at,
        updated_at=out.updated_at,
        completion_percentage=out.completion_percentage,
    )


@router.get("", response_model=list[TaskListResponse])
async def list_lists(
    current: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[TaskListResponse]:
    tlr = SQLAlchemyTaskListRepository(session)
    tr = SQLAlchemyTaskRepository(session)
    get_one = GetTaskList(tlr, tr)
    lists = await tlr.find_all_by_owner(current.id)
    res: list[TaskListResponse] = []
    for item in lists:
        out = await get_one.execute(
            GetTaskListInput(
                task_list_id=item.id,
                requester_id=current.id,
            )
        )
        res.append(
            TaskListResponse(
                id=out.id,
                name=out.name,
                description=out.description,
                owner_id=out.owner_id,
                created_at=out.created_at,
                updated_at=out.updated_at,
                completion_percentage=out.completion_percentage,
            )
        )
    return res


@router.get("/{list_id}", response_model=TaskListResponse)
async def get_list(
    list_id: UUID,
    current: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> TaskListResponse:
    uc = GetTaskList(
        SQLAlchemyTaskListRepository(session),
        SQLAlchemyTaskRepository(session),
    )
    out = await uc.execute(
        GetTaskListInput(
            task_list_id=list_id,
            requester_id=current.id,
        )
    )
    return TaskListResponse(
        id=out.id,
        name=out.name,
        description=out.description,
        owner_id=out.owner_id,
        created_at=out.created_at,
        updated_at=out.updated_at,
        completion_percentage=out.completion_percentage,
    )


@router.put("/{list_id}", response_model=TaskListResponse)
async def update_list(
    list_id: UUID,
    body: TaskListUpdate,
    current: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> TaskListResponse:
    uc = UpdateTaskList(
        SQLAlchemyTaskListRepository(session),
        SQLAlchemyTaskRepository(session),
    )
    out = await uc.execute(
        UpdateTaskListInput(
            task_list_id=list_id,
            requester_id=current.id,
            name=body.name,
            description=body.description,
        )
    )
    return TaskListResponse(
        id=out.id,
        name=out.name,
        description=out.description,
        owner_id=out.owner_id,
        created_at=out.created_at,
        updated_at=out.updated_at,
        completion_percentage=out.completion_percentage,
    )


@router.delete(
    "/{list_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_list(
    list_id: UUID,
    current: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Response:
    uc = DeleteTaskList(SQLAlchemyTaskListRepository(session))
    await uc.execute(
        DeleteTaskListInput(
            task_list_id=list_id,
            requester_id=current.id,
        )
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
