"""Tracing implementation for Agile-PM."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Generator

from pydantic import BaseModel


class Span(BaseModel):
    """A tracing span."""

    name: str
    start_time: datetime
    end_time: datetime | None = None
    attributes: dict[str, Any] = {}
    events: list[dict[str, Any]] = []
    parent_id: str | None = None
    span_id: str = ""


class Tracer:
    """Tracer for Agile-PM operations."""

    def __init__(self, enabled: bool = True) -> None:
        """Initialize tracer.
        
        Args:
            enabled: Whether tracing is enabled
        """
        self.enabled = enabled
        self._spans: list[Span] = []
        self._current_span: Span | None = None
        self._logger = logging.getLogger("agile_pm.tracer")

    @contextmanager
    def span(self, name: str, **attributes) -> Generator[Span, None, None]:
        """Create a tracing span.
        
        Args:
            name: Span name
            **attributes: Span attributes
            
        Yields:
            The created span
        """
        if not self.enabled:
            yield Span(name=name, start_time=datetime.utcnow())
            return
        
        import uuid
        
        span = Span(
            name=name,
            start_time=datetime.utcnow(),
            attributes=attributes,
            parent_id=self._current_span.span_id if self._current_span else None,
            span_id=str(uuid.uuid4()),
        )
        
        previous_span = self._current_span
        self._current_span = span
        
        try:
            yield span
        finally:
            span.end_time = datetime.utcnow()
            self._spans.append(span)
            self._current_span = previous_span
            
            duration = (span.end_time - span.start_time).total_seconds()
            self._logger.debug(f"Span '{name}' completed in {duration:.3f}s")

    def add_event(self, name: str, **attributes) -> None:
        """Add an event to the current span.
        
        Args:
            name: Event name
            **attributes: Event attributes
        """
        if not self.enabled or self._current_span is None:
            return
        
        self._current_span.events.append({
            "name": name,
            "timestamp": datetime.utcnow().isoformat(),
            "attributes": attributes,
        })

    def get_spans(self) -> list[Span]:
        """Get all recorded spans.
        
        Returns:
            List of spans
        """
        return self._spans.copy()

    def clear(self) -> None:
        """Clear all recorded spans."""
        self._spans.clear()
        self._current_span = None

    def export_json(self) -> list[dict]:
        """Export spans as JSON.
        
        Returns:
            List of span dictionaries
        """
        return [span.model_dump() for span in self._spans]
