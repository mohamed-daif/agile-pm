"""Structured logging for agent operations."""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Optional
from contextlib import contextmanager
import threading

from pydantic import BaseModel, Field


class LogConfig(BaseModel):
    """Configuration for structured logging."""

    level: str = Field(default="INFO")
    format: str = Field(default="json", description="json or text")
    include_trace: bool = Field(default=True)
    include_timestamp: bool = Field(default=True)
    
    # Output
    output: str = Field(default="stdout", description="stdout, stderr, or file path")
    file_rotation: bool = Field(default=True)
    max_file_size: int = Field(default=10 * 1024 * 1024)  # 10MB
    backup_count: int = Field(default=5)


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def __init__(self, include_trace: bool = True):
        super().__init__()
        self.include_trace = include_trace
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.
        
        Args:
            record: Log record
            
        Returns:
            JSON string
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add location info
        log_data["location"] = {
            "file": record.filename,
            "line": record.lineno,
            "function": record.funcName,
        }
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_data["extra"] = record.extra
        
        # Add context
        if hasattr(record, "context"):
            log_data["context"] = record.context
        
        # Add trace ID if available
        if self.include_trace:
            try:
                from opentelemetry import trace
                span = trace.get_current_span()
                if span:
                    context = span.get_span_context()
                    if context.is_valid:
                        log_data["trace_id"] = format(context.trace_id, '032x')
                        log_data["span_id"] = format(context.span_id, '016x')
            except ImportError:
                pass
        
        # Add exception info
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
            }
        
        return json.dumps(log_data, default=str)


class TextFormatter(logging.Formatter):
    """Human-readable text formatter."""

    def __init__(self, include_timestamp: bool = True):
        fmt = "%(levelname)s - %(name)s - %(message)s"
        if include_timestamp:
            fmt = "%(asctime)s - " + fmt
        super().__init__(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S")


class ContextAdapter(logging.LoggerAdapter):
    """Logger adapter that adds context to logs."""

    def process(self, msg: str, kwargs: dict) -> tuple[str, dict]:
        """Process log message with context.
        
        Args:
            msg: Log message
            kwargs: Keyword arguments
            
        Returns:
            Processed message and kwargs
        """
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs


class StructuredLogger:
    """Structured logger with context support."""

    _context = threading.local()

    def __init__(
        self,
        name: str,
        config: Optional[LogConfig] = None,
    ):
        """Initialize structured logger.
        
        Args:
            name: Logger name
            config: Log configuration
        """
        self.config = config or LogConfig()
        self._logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Set up logger with handlers."""
        level = getattr(logging, self.config.level.upper(), logging.INFO)
        self._logger.setLevel(level)
        
        # Remove existing handlers
        self._logger.handlers = []
        
        # Create formatter
        if self.config.format == "json":
            formatter = JsonFormatter(include_trace=self.config.include_trace)
        else:
            formatter = TextFormatter(include_timestamp=self.config.include_timestamp)
        
        # Create handler
        if self.config.output == "stdout":
            handler = logging.StreamHandler(sys.stdout)
        elif self.config.output == "stderr":
            handler = logging.StreamHandler(sys.stderr)
        else:
            if self.config.file_rotation:
                from logging.handlers import RotatingFileHandler
                handler = RotatingFileHandler(
                    self.config.output,
                    maxBytes=self.config.max_file_size,
                    backupCount=self.config.backup_count,
                )
            else:
                handler = logging.FileHandler(self.config.output)
        
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
    
    @contextmanager
    def context(self, **kwargs):
        """Add context to all logs in scope.
        
        Args:
            **kwargs: Context key-value pairs
        """
        if not hasattr(self._context, "stack"):
            self._context.stack = []
        
        self._context.stack.append(kwargs)
        try:
            yield
        finally:
            self._context.stack.pop()
    
    def _get_context(self) -> dict:
        """Get current context."""
        if not hasattr(self._context, "stack"):
            return {}
        
        merged = {}
        for ctx in self._context.stack:
            merged.update(ctx)
        return merged
    
    def _log(
        self,
        level: int,
        msg: str,
        *args,
        exc_info: bool = False,
        **kwargs,
    ) -> None:
        """Log with context.
        
        Args:
            level: Log level
            msg: Message
            *args: Format args
            exc_info: Include exception info
            **kwargs: Extra fields
        """
        extra = {"extra": kwargs, "context": self._get_context()}
        self._logger.log(level, msg, *args, exc_info=exc_info, extra=extra)
    
    def debug(self, msg: str, *args, **kwargs) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs) -> None:
        """Log info message."""
        self._log(logging.INFO, msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs) -> None:
        """Log warning message."""
        self._log(logging.WARNING, msg, *args, **kwargs)
    
    def error(self, msg: str, *args, exc_info: bool = False, **kwargs) -> None:
        """Log error message."""
        self._log(logging.ERROR, msg, *args, exc_info=exc_info, **kwargs)
    
    def exception(self, msg: str, *args, **kwargs) -> None:
        """Log exception with traceback."""
        self._log(logging.ERROR, msg, *args, exc_info=True, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, msg, *args, **kwargs)
    
    # Convenience methods for agent logging
    def agent_started(self, agent_id: str, role: str, **kwargs) -> None:
        """Log agent start."""
        self.info(
            "Agent started",
            agent_id=agent_id,
            agent_role=role,
            event="agent.started",
            **kwargs,
        )
    
    def agent_completed(
        self,
        agent_id: str,
        role: str,
        duration: float,
        success: bool,
        **kwargs,
    ) -> None:
        """Log agent completion."""
        level = logging.INFO if success else logging.WARNING
        self._log(
            level,
            "Agent completed",
            agent_id=agent_id,
            agent_role=role,
            duration_seconds=duration,
            success=success,
            event="agent.completed",
            **kwargs,
        )
    
    def task_started(self, task_id: str, title: str, **kwargs) -> None:
        """Log task start."""
        self.info(
            "Task started",
            task_id=task_id,
            task_title=title,
            event="task.started",
            **kwargs,
        )
    
    def task_completed(
        self,
        task_id: str,
        title: str,
        duration: float,
        success: bool,
        **kwargs,
    ) -> None:
        """Log task completion."""
        level = logging.INFO if success else logging.WARNING
        self._log(
            level,
            "Task completed",
            task_id=task_id,
            task_title=title,
            duration_seconds=duration,
            success=success,
            event="task.completed",
            **kwargs,
        )
    
    def llm_call(
        self,
        model: str,
        duration: float,
        tokens: int,
        **kwargs,
    ) -> None:
        """Log LLM API call."""
        self.debug(
            "LLM call",
            model=model,
            duration_seconds=duration,
            tokens=tokens,
            event="llm.call",
            **kwargs,
        )


# Global logger cache
_loggers: dict[str, StructuredLogger] = {}
_default_config: Optional[LogConfig] = None


def configure_logging(config: LogConfig) -> None:
    """Configure default logging.
    
    Args:
        config: Log configuration
    """
    global _default_config
    _default_config = config


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger.
    
    Args:
        name: Logger name
        
    Returns:
        Structured logger
    """
    if name not in _loggers:
        _loggers[name] = StructuredLogger(name, _default_config)
    return _loggers[name]
