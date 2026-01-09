"""Memory management endpoints."""
from typing import Optional, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter()

class MemoryCreate(BaseModel):
    key: str = Field(..., min_length=1, max_length=200)
    value: Any
    namespace: str = Field("default", min_length=1, max_length=50)
    ttl: Optional[int] = Field(None, ge=0)

class MemoryResponse(BaseModel):
    key: str
    value: Any
    namespace: str
    created_at: datetime
    expires_at: Optional[datetime]

@router.get("")
async def list_memories(namespace: str = Query("default"), pattern: str = Query("*")):
    """List memory keys."""
    return {"namespace": namespace, "pattern": pattern, "keys": []}

@router.post("", response_model=MemoryResponse, status_code=201)
async def create_memory(memory: MemoryCreate):
    """Store value in memory."""
    return MemoryResponse(
        key=memory.key, value=memory.value, namespace=memory.namespace,
        created_at=datetime.utcnow(), expires_at=None
    )

@router.get("/{key}", response_model=MemoryResponse)
async def get_memory(key: str, namespace: str = Query("default")):
    """Get memory value."""
    raise HTTPException(status_code=404, detail=f"Key {key} not found")

@router.delete("/{key}", status_code=204)
async def delete_memory(key: str, namespace: str = Query("default")):
    """Delete memory key."""
    raise HTTPException(status_code=404, detail=f"Key {key} not found")
