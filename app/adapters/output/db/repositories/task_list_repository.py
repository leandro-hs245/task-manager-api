from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.output.db.models.task_list import TaskListModel
from app.domain.entities.task_list import TaskList
from app.domain.exceptions.task_list import TaskListNotFoundException
from app.ports.output.task_list_repository import ITaskListRepository


class SQLAlchemyTaskListRepository(ITaskListRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def to_domain(m: TaskListModel) -> TaskList:
        return TaskList(
            id=m.id,
            name=m.name,
            description=m.description,
            owner_id=m.owner_id,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    @staticmethod
    def to_orm(e: TaskList) -> TaskListModel:
        return TaskListModel(
            id=e.id,
            name=e.name,
            description=e.description,
            owner_id=e.owner_id,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )

    async def save(self, task_list: TaskList) -> TaskList:
        m = self.to_orm(task_list)
        self._session.add(m)
        await self._session.flush()
        return self.to_domain(m)

    async def find_by_id(self, task_list_id: UUID) -> TaskList:
        m = await self._session.get(TaskListModel, task_list_id)
        if m is None:
            raise TaskListNotFoundException("Task list not found")
        return self.to_domain(m)

    async def find_all_by_owner(self, owner_id: UUID) -> list[TaskList]:
        q = await self._session.execute(
            select(TaskListModel)
            .where(TaskListModel.owner_id == owner_id)
            .order_by(TaskListModel.created_at)
        )
        return [self.to_domain(m) for m in q.scalars().all()]

    async def update(self, task_list: TaskList) -> TaskList:
        m = await self._session.get(TaskListModel, task_list.id)
        if m is None:
            raise TaskListNotFoundException("Task list not found")
        m.name = task_list.name
        m.description = task_list.description
        m.updated_at = task_list.updated_at
        await self._session.flush()
        return self.to_domain(m)

    async def delete(self, task_list_id: UUID) -> None:
        m = await self._session.get(TaskListModel, task_list_id)
        if m is None:
            raise TaskListNotFoundException("Task list not found")
        await self._session.delete(m)
        await self._session.flush()
