from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.output.db.models.task import TaskModel
from app.domain.entities.task import Task
from app.domain.exceptions.task import TaskNotFoundException
from app.domain.value_objects.priority import TaskPriority
from app.domain.value_objects.status import TaskStatus
from app.ports.output.task_repository import ITaskRepository


class SQLAlchemyTaskRepository(ITaskRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def to_domain(m: TaskModel) -> Task:
        return Task(
            id=m.id,
            title=m.title,
            description=m.description,
            status=TaskStatus(m.status),
            priority=TaskPriority(m.priority),
            task_list_id=m.task_list_id,
            assigned_user_id=m.assigned_user_id,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    @staticmethod
    def to_orm(e: Task) -> TaskModel:
        return TaskModel(
            id=e.id,
            title=e.title,
            description=e.description,
            status=e.status.value,
            priority=e.priority.value,
            task_list_id=e.task_list_id,
            assigned_user_id=e.assigned_user_id,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )

    async def save(self, task: Task) -> Task:
        m = self.to_orm(task)
        self._session.add(m)
        await self._session.flush()
        return self.to_domain(m)

    async def find_by_id(self, task_id: UUID) -> Task:
        m = await self._session.get(TaskModel, task_id)
        if m is None:
            raise TaskNotFoundException("Task not found")
        return self.to_domain(m)

    async def find_all_by_list_id(
        self,
        task_list_id: UUID,
        status: TaskStatus | None,
        priority: TaskPriority | None,
    ) -> list[Task]:
        cond = [TaskModel.task_list_id == task_list_id]
        if status is not None:
            cond.append(TaskModel.status == status.value)
        if priority is not None:
            cond.append(TaskModel.priority == priority.value)
        q = await self._session.execute(
            select(TaskModel)
            .where(and_(*cond))
            .order_by(TaskModel.created_at)
        )
        return [self.to_domain(m) for m in q.scalars().all()]

    async def update(self, task: Task) -> Task:
        m = await self._session.get(TaskModel, task.id)
        if m is None:
            raise TaskNotFoundException("Task not found")
        m.title = task.title
        m.description = task.description
        m.status = task.status.value
        m.priority = task.priority.value
        m.task_list_id = task.task_list_id
        m.assigned_user_id = task.assigned_user_id
        m.updated_at = task.updated_at
        await self._session.flush()
        return self.to_domain(m)

    async def delete(self, task_id: UUID) -> None:
        m = await self._session.get(TaskModel, task_id)
        if m is None:
            raise TaskNotFoundException("Task not found")
        await self._session.delete(m)
        await self._session.flush()
