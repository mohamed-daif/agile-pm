"""Jira field mapping."""
from typing import Any, Optional

class FieldMapper:
    DEFAULT_MAPPINGS = {
        "priority": {"P0": "Highest", "P1": "High", "P2": "Medium", "P3": "Low"},
        "status": {"todo": "To Do", "in_progress": "In Progress", "completed": "Done", "failed": "Done"}
    }
    
    def __init__(self, custom_mappings: dict = None):
        self.mappings = {**self.DEFAULT_MAPPINGS, **(custom_mappings or {})}
    
    def map_priority(self, priority: str) -> str:
        return self.mappings.get("priority", {}).get(priority, "Medium")
    
    def map_status(self, status: str) -> str:
        return self.mappings.get("status", {}).get(status, status)
    
    def map_custom_field(self, field_id: str, value: Any) -> dict:
        return {field_id: value}
