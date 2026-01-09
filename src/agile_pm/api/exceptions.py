"""Custom exception classes and error handling."""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class AgilePMException(Exception):
    """Base exception for Agile-PM."""
    
    code: str = "INTERNAL_ERROR"
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code or self.code
        self.details = details
        super().__init__(message)
    
    def to_http_exception(self) -> HTTPException:
        """Convert to FastAPI HTTPException."""
        return HTTPException(
            status_code=self.status_code,
            detail={
                "code": self.code,
                "message": self.message,
                "details": self.details,
            },
        )


# 4xx Client Errors

class BadRequestError(AgilePMException):
    """Invalid request data."""
    code = "BAD_REQUEST"
    status_code = status.HTTP_400_BAD_REQUEST


class ValidationError(AgilePMException):
    """Validation failed."""
    code = "VALIDATION_ERROR"
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class UnauthorizedError(AgilePMException):
    """Authentication required."""
    code = "UNAUTHORIZED"
    status_code = status.HTTP_401_UNAUTHORIZED


class ForbiddenError(AgilePMException):
    """Access denied."""
    code = "FORBIDDEN"
    status_code = status.HTTP_403_FORBIDDEN


class NotFoundError(AgilePMException):
    """Resource not found."""
    code = "NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND


class ConflictError(AgilePMException):
    """Resource conflict."""
    code = "CONFLICT"
    status_code = status.HTTP_409_CONFLICT


class RateLimitError(AgilePMException):
    """Rate limit exceeded."""
    code = "RATE_LIMITED"
    status_code = status.HTTP_429_TOO_MANY_REQUESTS


# 5xx Server Errors

class InternalError(AgilePMException):
    """Internal server error."""
    code = "INTERNAL_ERROR"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class ServiceUnavailableError(AgilePMException):
    """Service temporarily unavailable."""
    code = "SERVICE_UNAVAILABLE"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class DatabaseError(AgilePMException):
    """Database operation failed."""
    code = "DATABASE_ERROR"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class ExternalServiceError(AgilePMException):
    """External service call failed."""
    code = "EXTERNAL_SERVICE_ERROR"
    status_code = status.HTTP_502_BAD_GATEWAY


# Business Logic Errors

class AgentNotReadyError(AgilePMException):
    """Agent is not ready for operations."""
    code = "AGENT_NOT_READY"
    status_code = status.HTTP_409_CONFLICT


class TaskAlreadyAssignedError(AgilePMException):
    """Task is already assigned."""
    code = "TASK_ALREADY_ASSIGNED"
    status_code = status.HTTP_409_CONFLICT


class SprintLockedError(AgilePMException):
    """Sprint is locked and cannot be modified."""
    code = "SPRINT_LOCKED"
    status_code = status.HTTP_409_CONFLICT


class WebhookDeliveryError(AgilePMException):
    """Webhook delivery failed."""
    code = "WEBHOOK_DELIVERY_FAILED"
    status_code = status.HTTP_502_BAD_GATEWAY


class PluginError(AgilePMException):
    """Plugin operation failed."""
    code = "PLUGIN_ERROR"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class ConfigurationError(AgilePMException):
    """Configuration is invalid."""
    code = "CONFIGURATION_ERROR"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
