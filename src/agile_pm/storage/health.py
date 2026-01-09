"""Health check utilities."""
from dataclasses import dataclass
from typing import Optional
from agile_pm.storage.database import get_db
from agile_pm.storage.redis import get_redis

@dataclass
class HealthStatus:
    healthy: bool
    database: bool
    redis: bool
    message: Optional[str] = None

async def check_database() -> bool:
    try:
        db = get_db()
        async with db.session() as session:
            await session.execute("SELECT 1")
        return True
    except Exception:
        return False

async def check_redis() -> bool:
    try:
        redis = get_redis()
        return await redis.ping()
    except Exception:
        return False

async def check_all() -> HealthStatus:
    db_ok = await check_database()
    redis_ok = await check_redis()
    return HealthStatus(
        healthy=db_ok and redis_ok,
        database=db_ok,
        redis=redis_ok,
    )
