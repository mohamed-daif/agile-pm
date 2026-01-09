"""Input Validation and Sanitization."""

import re
from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of validation."""
    is_valid: bool
    error: Optional[str] = None
    sanitized: Optional[Any] = None


class InputValidator:
    """Validate and sanitize user inputs."""

    # Patterns
    SAFE_STRING_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\s\.\,\!\?]+$")
    IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")
    API_KEY_PATTERN = re.compile(r"^sk-[a-zA-Z0-9]{48,}$")
    
    # Limits
    MAX_STRING_LENGTH = 10000
    MAX_IDENTIFIER_LENGTH = 128
    MAX_LIST_SIZE = 100
    MAX_OBJECT_DEPTH = 10

    @classmethod
    def validate_string(
        cls,
        value: str,
        max_length: int = MAX_STRING_LENGTH,
        allow_html: bool = False,
        allow_newlines: bool = True,
    ) -> ValidationResult:
        """Validate and sanitize string input."""
        if not isinstance(value, str):
            return ValidationResult(False, "Value must be a string")
        
        if len(value) > max_length:
            return ValidationResult(False, f"Value exceeds max length {max_length}")
        
        sanitized = value
        
        # Remove null bytes
        sanitized = sanitized.replace("\x00", "")
        
        # Strip HTML if not allowed
        if not allow_html:
            sanitized = re.sub(r"<[^>]+>", "", sanitized)
        
        # Remove control characters (except newline if allowed)
        if allow_newlines:
            sanitized = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", sanitized)
        else:
            sanitized = re.sub(r"[\x00-\x1f\x7f]", "", sanitized)
        
        return ValidationResult(True, sanitized=sanitized)

    @classmethod
    def validate_identifier(cls, value: str) -> ValidationResult:
        """Validate identifier (task ID, agent ID, etc.)."""
        if not isinstance(value, str):
            return ValidationResult(False, "Identifier must be a string")
        
        if len(value) > cls.MAX_IDENTIFIER_LENGTH:
            return ValidationResult(False, f"Identifier too long (max {cls.MAX_IDENTIFIER_LENGTH})")
        
        if not cls.IDENTIFIER_PATTERN.match(value):
            return ValidationResult(False, "Invalid identifier format")
        
        return ValidationResult(True, sanitized=value)

    @classmethod
    def validate_api_key(cls, value: str) -> ValidationResult:
        """Validate API key format."""
        if not isinstance(value, str):
            return ValidationResult(False, "API key must be a string")
        
        # Check pattern for OpenAI-style keys
        if value.startswith("sk-"):
            if not cls.API_KEY_PATTERN.match(value):
                return ValidationResult(False, "Invalid API key format")
        
        return ValidationResult(True, sanitized=value)

    @classmethod
    def validate_json_depth(cls, obj: Any, current_depth: int = 0) -> ValidationResult:
        """Validate JSON object doesn't exceed max nesting depth."""
        if current_depth > cls.MAX_OBJECT_DEPTH:
            return ValidationResult(False, f"Object depth exceeds {cls.MAX_OBJECT_DEPTH}")
        
        if isinstance(obj, dict):
            for v in obj.values():
                result = cls.validate_json_depth(v, current_depth + 1)
                if not result.is_valid:
                    return result
        elif isinstance(obj, list):
            if len(obj) > cls.MAX_LIST_SIZE:
                return ValidationResult(False, f"List size exceeds {cls.MAX_LIST_SIZE}")
            for item in obj:
                result = cls.validate_json_depth(item, current_depth + 1)
                if not result.is_valid:
                    return result
        
        return ValidationResult(True, sanitized=obj)


def sanitize_log_message(message: str, sensitive_fields: set = None) -> str:
    """Sanitize log messages to remove sensitive data."""
    from .config import SENSITIVE_FIELDS
    
    fields = sensitive_fields or SENSITIVE_FIELDS
    sanitized = message
    
    for field in fields:
        # Match patterns like field="value" or field=value or "field": "value"
        patterns = [
            rf'{field}="[^"]*"',
            rf'{field}=[^\s,}}]+',
            rf'"{field}":\s*"[^"]*"',
        ]
        for pattern in patterns:
            sanitized = re.sub(pattern, f'{field}="[REDACTED]"', sanitized, flags=re.IGNORECASE)
    
    return sanitized
