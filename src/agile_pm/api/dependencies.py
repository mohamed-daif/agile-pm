"""API dependencies for dependency injection."""
from typing import AsyncGenerator
from agile_pm.storage.database import get_db
from agile_pm.storage.repositories.unit_of_work import UnitOfWork

async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    """Get unit of work for request."""
    async with UnitOfWork() as uow:
        yield uow
