"""Agent repository."""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from agile_pm.storage.models import AgentModel
from agile_pm.storage.repositories.base import BaseRepository

class AgentRepository(BaseRepository[AgentModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AgentModel)
    
    async def get_by_name(self, name: str) -> Optional[AgentModel]:
        result = await self.session.execute(
            select(AgentModel).where(AgentModel.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_by_type(self, agent_type: str) -> List[AgentModel]:
        result = await self.session.execute(
            select(AgentModel).where(AgentModel.type == agent_type)
        )
        return list(result.scalars().all())
    
    async def get_active(self) -> List[AgentModel]:
        result = await self.session.execute(
            select(AgentModel).where(AgentModel.status == "active")
        )
        return list(result.scalars().all())
