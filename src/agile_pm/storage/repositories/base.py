"""Base repository class."""
from typing import TypeVar, Generic, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model
    
    async def get(self, id: str) -> Optional[T]:
        return await self.session.get(self.model, id)
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        result = await self.session.execute(
            select(self.model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())
    
    async def create(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        return entity
    
    async def update(self, entity: T) -> T:
        await self.session.flush()
        return entity
    
    async def delete(self, id: str) -> bool:
        entity = await self.get(id)
        if entity:
            await self.session.delete(entity)
            return True
        return False
