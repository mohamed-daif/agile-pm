"""Pagination utilities for API endpoints."""
from typing import Generic, TypeVar, List, Optional, Tuple
from base64 import b64encode, b64decode
from pydantic import BaseModel, Field
from fastapi import Query

T = TypeVar("T")


class PageParams(BaseModel):
    """Page-based pagination parameters."""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    
    @property
    def skip(self) -> int:
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        return self.page_size


class CursorParams(BaseModel):
    """Cursor-based pagination parameters."""
    cursor: Optional[str] = Field(None, description="Pagination cursor")
    limit: int = Field(20, ge=1, le=100, description="Items to return")
    direction: str = Field("next", regex="^(next|prev)$")


class Page(BaseModel, Generic[T]):
    """Page-based pagination response."""
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        params: PageParams,
    ) -> "Page[T]":
        pages = max(1, (total + params.page_size - 1) // params.page_size)
        return cls(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=pages,
            has_next=params.page < pages,
            has_prev=params.page > 1,
        )


class CursorPage(BaseModel, Generic[T]):
    """Cursor-based pagination response."""
    items: List[T]
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None
    has_more: bool = False
    
    @classmethod
    def create(
        cls,
        items: List[T],
        cursor_field: str,
        limit: int,
        has_more: bool,
    ) -> "CursorPage[T]":
        next_cursor = None
        if items and has_more:
            last_item = items[-1]
            cursor_value = getattr(last_item, cursor_field, None)
            if cursor_value:
                next_cursor = encode_cursor(str(cursor_value))
        
        return cls(
            items=items,
            next_cursor=next_cursor,
            has_more=has_more,
        )


def encode_cursor(value: str) -> str:
    """Encode a cursor value."""
    return b64encode(value.encode()).decode()


def decode_cursor(cursor: str) -> str:
    """Decode a cursor value."""
    try:
        return b64decode(cursor.encode()).decode()
    except Exception:
        return ""


def get_page_params(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize", description="Items per page"),
) -> PageParams:
    """Dependency for page-based pagination."""
    return PageParams(page=page, page_size=page_size)


def get_cursor_params(
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    limit: int = Query(20, ge=1, le=100, description="Items to return"),
) -> CursorParams:
    """Dependency for cursor-based pagination."""
    return CursorParams(cursor=cursor, limit=limit)


class Paginator(Generic[T]):
    """Helper class for paginating query results."""
    
    def __init__(self, items: List[T], total: int):
        self.items = items
        self.total = total
    
    def as_page(self, params: PageParams) -> Page[T]:
        """Convert to page response."""
        return Page.create(self.items, self.total, params)
    
    def as_cursor_page(
        self,
        cursor_field: str,
        limit: int,
    ) -> CursorPage[T]:
        """Convert to cursor page response."""
        has_more = len(self.items) > limit
        items = self.items[:limit] if has_more else self.items
        return CursorPage.create(items, cursor_field, limit, has_more)
