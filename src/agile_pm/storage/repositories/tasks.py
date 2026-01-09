"""Task repository."""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from agile_pm.storage.models import TaskModel
from agile_pm.storage.repositories.base import BaseRepository

class TaskRepository(BaseRepository[TaskModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, TaskModel)
    
    async def get_by_status(self, status: str) -> List[TaskModel]:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.status == status)
        )
        return list(result.scalars().all())
    
    async def get_by_sprint(self, sprint_id: str) -> List[TaskModel]:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.sprint_id == sprint_id)
        )
        return list(result.scalars().all())
    
    async def get_by_agent(self, agent_id: str) -> List[TaskModel]:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.agent_id == agent_id)
        )
        return list(result.scalars().all())
