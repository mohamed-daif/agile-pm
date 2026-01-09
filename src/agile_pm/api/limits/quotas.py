"""Usage quota management."""
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass
from enum import Enum

class QuotaTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

QUOTA_LIMITS = {
    QuotaTier.FREE: {"daily": 1000, "monthly": 10000},
    QuotaTier.BASIC: {"daily": 10000, "monthly": 100000},
    QuotaTier.PRO: {"daily": 100000, "monthly": 1000000},
    QuotaTier.ENTERPRISE: {"daily": -1, "monthly": -1}
}

@dataclass
class QuotaStatus:
    tier: QuotaTier
    daily_limit: int
    daily_used: int
    daily_remaining: int
    monthly_limit: int
    monthly_used: int
    monthly_remaining: int
    daily_reset: datetime
    monthly_reset: datetime

class QuotaManager:
    def __init__(self):
        self._usage: dict = {}
    
    def _get_user_data(self, user_id: str) -> dict:
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if user_id not in self._usage:
            self._usage[user_id] = {
                "tier": QuotaTier.FREE,
                "daily_count": 0,
                "daily_reset": today + timedelta(days=1),
                "monthly_count": 0,
                "monthly_reset": (month_start + timedelta(days=32)).replace(day=1)
            }
        
        data = self._usage[user_id]
        if now >= data["daily_reset"]:
            data["daily_count"] = 0
            data["daily_reset"] = today + timedelta(days=1)
        if now >= data["monthly_reset"]:
            data["monthly_count"] = 0
            data["monthly_reset"] = (month_start + timedelta(days=32)).replace(day=1)
        
        return data
    
    def check_quota(self, user_id: str) -> tuple:
        data = self._get_user_data(user_id)
        limits = QUOTA_LIMITS[data["tier"]]
        
        daily_ok = limits["daily"] == -1 or data["daily_count"] < limits["daily"]
        monthly_ok = limits["monthly"] == -1 or data["monthly_count"] < limits["monthly"]
        
        return daily_ok and monthly_ok, self.get_status(user_id)
    
    def increment(self, user_id: str) -> None:
        data = self._get_user_data(user_id)
        data["daily_count"] += 1
        data["monthly_count"] += 1
    
    def get_status(self, user_id: str) -> QuotaStatus:
        data = self._get_user_data(user_id)
        limits = QUOTA_LIMITS[data["tier"]]
        return QuotaStatus(
            tier=data["tier"],
            daily_limit=limits["daily"],
            daily_used=data["daily_count"],
            daily_remaining=max(0, limits["daily"] - data["daily_count"]) if limits["daily"] != -1 else -1,
            monthly_limit=limits["monthly"],
            monthly_used=data["monthly_count"],
            monthly_remaining=max(0, limits["monthly"] - data["monthly_count"]) if limits["monthly"] != -1 else -1,
            daily_reset=data["daily_reset"],
            monthly_reset=data["monthly_reset"]
        )
    
    def set_tier(self, user_id: str, tier: QuotaTier) -> None:
        data = self._get_user_data(user_id)
        data["tier"] = tier
