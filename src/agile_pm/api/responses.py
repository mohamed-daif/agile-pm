"""Standardized API response models."""
from typing import Generic, TypeVar, Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Error detail structure."""
    code: str
    message: str
    field: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class APIResponse(BaseModel, Generic[T]):
    """Standard API response envelope."""
    success: bool = True
    data: Optional[T] = None
    errors: Optional[List[ErrorDetail]] = None
    meta: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"id": "123", "name": "Example"},
                "meta": {"version": "1.0.0"},
                "timestamp": "2026-01-10T12:00:00Z",
                "request_id": "req-abc123",
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response."""
    items: List[T]
    total: int
    page: int = 1
    page_size: int = 20
    pages: int = 1
    has_next: bool = False
    has_prev: bool = False
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int = 1,
        page_size: int = 20,
    ) -> "PaginatedResponse[T]":
        pages = (total + page_size - 1) // page_size if page_size > 0 else 1
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1,
        )


class ErrorResponse(BaseModel):
    """Error response structure."""
    success: bool = False
    errors: List[ErrorDetail]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None
    trace_id: Optional[str] = None

    @classmethod
    def from_exception(
        cls,
        code: str,
        message: str,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> "ErrorResponse":
        return cls(
            errors=[
                ErrorDetail(code=code, message=message, details=details)
            ],
            request_id=request_id,
        )


# Convenience response creators
def success_response(
    data: Any = None,
    meta: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> APIResponse:
    """Create a success response."""
    return APIResponse(
        success=True,
        data=data,
        meta=meta,
        request_id=request_id,
    )


def error_response(
    code: str,
    message: str,
    request_id: Optional[str] = None,
    status_code: int = 400,
) -> ErrorResponse:
    """Create an error response."""
    return ErrorResponse.from_exception(
        code=code,
        message=message,
        request_id=request_id,
    )


# Error codes catalog
class ErrorCodes:
    """Standard error codes."""
    # 4xx Client Errors
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    
    # 5xx Server Errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    
    # Business Errors
    AGENT_NOT_READY = "AGENT_NOT_READY"
    TASK_ALREADY_ASSIGNED = "TASK_ALREADY_ASSIGNED"
    SPRINT_LOCKED = "SPRINT_LOCKED"
    WEBHOOK_DELIVERY_FAILED = "WEBHOOK_DELIVERY_FAILED"
