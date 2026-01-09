"""Database connection management."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from agile_pm.storage.models import Base


class Database:
    """Async database manager."""
    
    def __init__(self, url: str, pool_size: int = 20, echo: bool = False):
        self.url = url
        self._engine = create_async_engine(
            url,
            pool_size=pool_size,
            max_overflow=10,
            echo=echo,
        )
        self._session_factory = async_sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def create_tables(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_tables(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def close(self) -> None:
        await self._engine.dispose()


_db: Database | None = None

def init_db(url: str, **kwargs) -> Database:
    global _db
    _db = Database(url, **kwargs)
    return _db

def get_db() -> Database:
    if _db is None:
        raise RuntimeError("Database not initialized")
    return _db
