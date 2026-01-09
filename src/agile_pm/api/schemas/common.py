"""Common API schemas."""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: list
    total: int
    skip: int
    limit: int
    has_more: bool

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None
