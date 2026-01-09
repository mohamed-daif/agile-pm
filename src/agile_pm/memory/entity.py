"""Entity memory for extracting and tracking entities.

Provides entity extraction and tracking for project context.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field


class EntityInfo(BaseModel):
    """Information about an extracted entity."""

    name: str
    type: str = Field(description="Entity type: person, project, technology, etc.")
    description: str = Field(default="")
    attributes: dict[str, Any] = Field(default_factory=dict)
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    mentions: int = Field(default=1)


class EntityConfig(BaseModel):
    """Configuration for entity memory."""

    max_entities: int = Field(default=100, ge=10, le=1000)
    entity_types: list[str] = Field(
        default_factory=lambda: [
            "person",
            "project",
            "technology",
            "file",
            "task",
            "sprint",
            "feature",
        ]
    )
    extraction_prompt: Optional[str] = None


# Default extraction prompt
DEFAULT_EXTRACTION_PROMPT = """Extract entities from the following conversation.
Identify: people, projects, technologies, files, tasks, sprints, and features.

Conversation:
{history}

Extract entities in the format:
- Entity Name | Type | Brief Description

Entities:"""


class EntityMemory:
    """Entity extraction and tracking memory.
    
    Tracks entities mentioned across conversations:
    - People (team members, stakeholders)
    - Projects and features
    - Technologies and files
    - Tasks and sprints
    """

    def __init__(
        self,
        llm: BaseChatModel,
        session_id: Optional[str] = None,
        config: Optional[EntityConfig] = None,
    ):
        """Initialize entity memory.
        
        Args:
            llm: Language model for entity extraction
            session_id: Optional session identifier
            config: Memory configuration
        """
        self.session_id = session_id or str(uuid4())
        self.config = config or EntityConfig()
        self.llm = llm
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        self._entities: dict[str, EntityInfo] = {}
        self._extraction_prompt = PromptTemplate(
            input_variables=["history"],
            template=self.config.extraction_prompt or DEFAULT_EXTRACTION_PROMPT,
        )
    
    @property
    def entities(self) -> dict[str, EntityInfo]:
        """Get all tracked entities."""
        return self._entities
    
    @property
    def entity_count(self) -> int:
        """Get number of tracked entities."""
        return len(self._entities)
    
    def get_entity(self, name: str) -> Optional[EntityInfo]:
        """Get entity by name.
        
        Args:
            name: Entity name (case-insensitive)
            
        Returns:
            EntityInfo if found, None otherwise
        """
        return self._entities.get(name.lower())
    
    def add_entity(
        self,
        name: str,
        entity_type: str,
        description: str = "",
        attributes: Optional[dict[str, Any]] = None,
    ) -> EntityInfo:
        """Add or update an entity.
        
        Args:
            name: Entity name
            entity_type: Type of entity
            description: Optional description
            attributes: Optional attributes dict
            
        Returns:
            Created or updated EntityInfo
        """
        key = name.lower()
        
        if key in self._entities:
            # Update existing entity
            entity = self._entities[key]
            entity.mentions += 1
            entity.last_updated = datetime.utcnow()
            if description:
                entity.description = description
            if attributes:
                entity.attributes.update(attributes)
        else:
            # Create new entity
            entity = EntityInfo(
                name=name,
                type=entity_type,
                description=description,
                attributes=attributes or {},
            )
            self._entities[key] = entity
            self._trim_if_needed()
        
        self.updated_at = datetime.utcnow()
        return entity
    
    def remove_entity(self, name: str) -> bool:
        """Remove an entity.
        
        Args:
            name: Entity name
            
        Returns:
            True if removed, False if not found
        """
        key = name.lower()
        if key in self._entities:
            del self._entities[key]
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def get_entities_by_type(self, entity_type: str) -> list[EntityInfo]:
        """Get all entities of a specific type.
        
        Args:
            entity_type: Type to filter by
            
        Returns:
            List of matching entities
        """
        return [e for e in self._entities.values() if e.type == entity_type]
    
    async def extract_entities(self, text: str) -> list[EntityInfo]:
        """Extract entities from text using LLM.
        
        Args:
            text: Text to extract entities from
            
        Returns:
            List of extracted entities
        """
        prompt = self._extraction_prompt.format(history=text)
        response = await self.llm.ainvoke(prompt)
        
        # Parse response and extract entities
        extracted: list[EntityInfo] = []
        for line in response.content.split("\n"):
            line = line.strip()
            if line.startswith("-") and "|" in line:
                parts = [p.strip() for p in line[1:].split("|")]
                if len(parts) >= 2:
                    name = parts[0]
                    entity_type = parts[1].lower()
                    description = parts[2] if len(parts) > 2 else ""
                    
                    if entity_type in self.config.entity_types:
                        entity = self.add_entity(name, entity_type, description)
                        extracted.append(entity)
        
        return extracted
    
    def get_context_string(self) -> str:
        """Get entities as context string for prompts.
        
        Returns:
            Formatted entity context
        """
        if not self._entities:
            return "No entities tracked yet."
        
        lines = ["Known entities:"]
        for entity_type in self.config.entity_types:
            entities = self.get_entities_by_type(entity_type)
            if entities:
                lines.append(f"\n{entity_type.title()}s:")
                for e in entities:
                    desc = f" - {e.description}" if e.description else ""
                    lines.append(f"  - {e.name}{desc}")
        
        return "\n".join(lines)
    
    def _trim_if_needed(self) -> None:
        """Remove oldest entities if exceeding max limit."""
        if self.entity_count > self.config.max_entities:
            # Sort by mentions (keep most mentioned) and last_updated
            sorted_entities = sorted(
                self._entities.items(),
                key=lambda x: (x[1].mentions, x[1].last_updated),
            )
            # Remove oldest/least mentioned
            excess = self.entity_count - self.config.max_entities
            for key, _ in sorted_entities[:excess]:
                del self._entities[key]
    
    def clear(self) -> None:
        """Clear all entities."""
        self._entities.clear()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.
        
        Returns:
            Dict representation
        """
        return {
            "session_id": self.session_id,
            "config": self.config.model_dump(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "entities": {
                key: {
                    "name": e.name,
                    "type": e.type,
                    "description": e.description,
                    "attributes": e.attributes,
                    "first_seen": e.first_seen.isoformat(),
                    "last_updated": e.last_updated.isoformat(),
                    "mentions": e.mentions,
                }
                for key, e in self._entities.items()
            },
        }
    
    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        llm: BaseChatModel,
    ) -> "EntityMemory":
        """Deserialize from dictionary.
        
        Args:
            data: Dict representation
            llm: Language model
            
        Returns:
            Restored EntityMemory
        """
        config = EntityConfig(**data.get("config", {}))
        memory = cls(llm=llm, session_id=data["session_id"], config=config)
        memory.created_at = datetime.fromisoformat(data["created_at"])
        memory.updated_at = datetime.fromisoformat(data["updated_at"])
        
        # Restore entities
        for key, entity_data in data.get("entities", {}).items():
            memory._entities[key] = EntityInfo(
                name=entity_data["name"],
                type=entity_data["type"],
                description=entity_data.get("description", ""),
                attributes=entity_data.get("attributes", {}),
                first_seen=datetime.fromisoformat(entity_data["first_seen"]),
                last_updated=datetime.fromisoformat(entity_data["last_updated"]),
                mentions=entity_data.get("mentions", 1),
            )
        
        return memory
