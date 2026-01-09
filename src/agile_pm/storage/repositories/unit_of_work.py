"""Unit of Work pattern."""
from agile_pm.storage.database import get_db
from agile_pm.storage.repositories.agents import AgentRepository
from agile_pm.storage.repositories.tasks import TaskRepository

class UnitOfWork:
    def __init__(self):
        self._session = None
        self.agents: AgentRepository = None
        self.tasks: TaskRepository = None
    
    async def __aenter__(self):
        db = get_db()
        self._session_ctx = db.session()
        self._session = await self._session_ctx.__aenter__()
        self.agents = AgentRepository(self._session)
        self.tasks = TaskRepository(self._session)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._session_ctx.__aexit__(exc_type, exc_val, exc_tb)
    
    async def commit(self):
        await self._session.commit()
    
    async def rollback(self):
        await self._session.rollback()
