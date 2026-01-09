"""
Agent Registry

Central registry for all Agile-PM agents. Provides:
- Agent registration and lookup
- Role switching coordination
- Factory methods for agent creation
- Capability queries across agents
"""

from pathlib import Path
from typing import Any, Optional, Type

from .base import (
    AgentType,
    BaseAgent,
    AgentCapability,
    CapabilityLevel,
)


class AgentRegistry:
    """
    Central registry for all Agile-PM agents.
    
    Manages agent registration, lookup, and role switching.
    Implements singleton pattern for global access.
    
    Usage:
        registry = AgentRegistry()
        registry.register(BackendEngineerAgent)
        agent = registry.get("backend-engineer")
    """
    
    _instance: Optional["AgentRegistry"] = None
    _agents: dict[str, Type[BaseAgent]] = {}
    _instances: dict[str, BaseAgent] = {}
    
    def __new__(cls) -> "AgentRegistry":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the registry."""
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._register_default_agents()
    
    def _register_default_agents(self) -> None:
        """Register all default agents from definitions."""
        # Import here to avoid circular imports
        from .definitions import ALL_AGENTS
        for agent_cls in ALL_AGENTS:
            self.register(agent_cls)
    
    def register(self, agent_cls: Type[BaseAgent]) -> None:
        """
        Register an agent class.
        
        Args:
            agent_cls: The agent class to register
        """
        self._agents[agent_cls.ROLE_ID] = agent_cls
    
    def unregister(self, role_id: str) -> None:
        """
        Unregister an agent.
        
        Args:
            role_id: The role ID to unregister
        """
        if role_id in self._agents:
            del self._agents[role_id]
        if role_id in self._instances:
            del self._instances[role_id]
    
    def get(
        self,
        role_id: str,
        llm: Optional[Any] = None,
        cached: bool = True,
    ) -> Optional[BaseAgent]:
        """
        Get an agent by role ID.
        
        Args:
            role_id: The role ID to lookup
            llm: Optional LLM to pass to agent
            cached: Whether to use cached instance
            
        Returns:
            Agent instance or None if not found
        """
        if role_id not in self._agents:
            return None
        
        if cached and role_id in self._instances:
            return self._instances[role_id]
        
        agent = self._agents[role_id](llm=llm)
        if cached:
            self._instances[role_id] = agent
        
        return agent
    
    def get_by_type(self, agent_type: AgentType) -> list[BaseAgent]:
        """
        Get all agents of a specific type.
        
        Args:
            agent_type: The agent type to filter by
            
        Returns:
            List of agents matching the type
        """
        return [
            self.get(role_id)
            for role_id, cls in self._agents.items()
            if cls.ROLE_TYPE == agent_type
        ]
    
    def get_with_capability(
        self,
        capability: str,
        level: CapabilityLevel = CapabilityLevel.EXECUTE,
    ) -> list[BaseAgent]:
        """
        Get all agents with a specific capability.
        
        Args:
            capability: The capability name to search for
            level: Minimum capability level required
            
        Returns:
            List of agents with the capability
        """
        matching = []
        for role_id in self._agents:
            agent = self.get(role_id)
            if agent and agent.can_perform(level.value, capability):
                matching.append(agent)
        return matching
    
    def list_all(self) -> list[dict[str, Any]]:
        """
        List all registered agents.
        
        Returns:
            List of agent metadata dictionaries
        """
        return [
            {
                "id": role_id,
                "name": cls.ROLE_NAME,
                "type": cls.ROLE_TYPE.value,
                "charter_section": cls.CHARTER_SECTION,
            }
            for role_id, cls in self._agents.items()
        ]
    
    def list_by_category(self) -> dict[str, list[dict[str, Any]]]:
        """
        List agents grouped by type category.
        
        Returns:
            Dictionary mapping type to list of agents
        """
        result: dict[str, list[dict[str, Any]]] = {
            "strategic": [],
            "executor": [],
            "specialist": [],
            "reviewer": [],
        }
        
        for role_id, cls in self._agents.items():
            result[cls.ROLE_TYPE.value].append({
                "id": role_id,
                "name": cls.ROLE_NAME,
                "charter_section": cls.CHARTER_SECTION,
            })
        
        return result
    
    def find_for_file(self, file_path: str) -> Optional[BaseAgent]:
        """
        Find the most appropriate agent for a given file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Most appropriate agent or None
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        name = path.name.lower()
        
        # Test files → QA
        if "test" in name or "spec" in name:
            return self.get("qa-executor")
        
        # Security files → Security
        if "security" in name or "auth" in name:
            return self.get("security-executor")
        
        # Infrastructure files → DevOps
        if suffix in [".yml", ".yaml"] and any(
            x in name for x in ["docker", "k8s", "ci", "workflow"]
        ):
            return self.get("devops-executor")
        
        # Frontend files
        if suffix in [".tsx", ".jsx", ".css", ".scss"]:
            return self.get("frontend-engineer")
        
        # Backend files
        if suffix in [".ts", ".js", ".py"]:
            # Check if it's in frontend directory
            if "frontend" in str(path):
                return self.get("frontend-engineer")
            return self.get("backend-engineer")
        
        # Documentation
        if suffix in [".md", ".mdx", ".rst"]:
            return self.get("technical-writer")
        
        # Default to fullstack
        return self.get("fullstack-engineer")
    
    def get_reviewer_for(self, agent: BaseAgent) -> Optional[BaseAgent]:
        """
        Get the appropriate reviewer for an agent's work.
        
        Args:
            agent: The agent whose work needs review
            
        Returns:
            Appropriate reviewer agent
        """
        role_type = agent.role_type
        role_id = agent.role_id
        
        # Map executor to reviewer
        reviewer_map = {
            "backend-engineer": "backend-reviewer",
            "frontend-engineer": "frontend-reviewer",
            "fullstack-engineer": "backend-reviewer",  # Primary reviewer
            "devops-executor": "devops-reviewer",
            "security-executor": "security-reviewer",
            "qa-executor": "backend-reviewer",  # QA reviewed by backend
        }
        
        reviewer_id = reviewer_map.get(role_id)
        if reviewer_id:
            return self.get(reviewer_id)
        
        # Default based on type
        if role_type == AgentType.EXECUTOR:
            return self.get("architecture-reviewer")
        
        return None
    
    def clear_cache(self) -> None:
        """Clear all cached agent instances."""
        self._instances.clear()
    
    @property
    def count(self) -> int:
        """Get the number of registered agents."""
        return len(self._agents)
    
    def __contains__(self, role_id: str) -> bool:
        """Check if an agent is registered."""
        return role_id in self._agents
    
    def __iter__(self):
        """Iterate over registered agent IDs."""
        return iter(self._agents)


# Module-level convenience functions
_registry: Optional[AgentRegistry] = None


def get_registry() -> AgentRegistry:
    """Get the global agent registry instance."""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry


def get_agent(role_id: str, llm: Optional[Any] = None) -> Optional[BaseAgent]:
    """
    Get an agent by role ID.
    
    Args:
        role_id: The role ID to lookup
        llm: Optional LLM to pass to agent
        
    Returns:
        Agent instance or None
    """
    return get_registry().get(role_id, llm=llm)


def list_agents() -> list[dict[str, Any]]:
    """
    List all registered agents.
    
    Returns:
        List of agent metadata
    """
    return get_registry().list_all()
