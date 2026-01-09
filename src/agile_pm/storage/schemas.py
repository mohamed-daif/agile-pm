"""Pydantic schemas for database models."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class AgentSchema(BaseModel):
    id: str
    name: str
    type: str
    status: str = "active"
    capabilities: List[str] = []
    config: dict = {}
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskSchema(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    status: str = "not-started"
    priority: str = "P1"
    agent_id: Optional[str] = None
    sprint_id: Optional[str] = None
    story_points: Optional[int] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SprintSchema(BaseModel):
    id: str
    name: str
    goal: Optional[str] = None
    status: str = "planning"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total_points: int = 0
    completed_points: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
