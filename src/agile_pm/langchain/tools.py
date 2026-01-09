"""Tool definitions for Agile-PM agents.

This module provides LangChain tool wrappers for:
- Obsidian vault operations
- GitHub MCP interactions
- Serena code analysis
- File system operations
"""

from typing import Any, Optional, Type

from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel, Field


# Tool registries
_tool_registry: dict[str, Type[BaseTool]] = {}


def register_tool(tool_class: Type[BaseTool]) -> Type[BaseTool]:
    """Decorator to register a tool class.
    
    Note: Uses the class's 'name' attribute defined as a class variable.
    For Pydantic v2 compatibility, we instantiate briefly to get the name.
    """
    # Create a temporary instance to get the name (Pydantic v2 compatible)
    try:
        tool_name = getattr(tool_class, 'name', None)
        if tool_name is None:
            # Fallback to class name
            tool_name = tool_class.__name__.lower()
        _tool_registry[tool_name] = tool_class
    except Exception:
        # If instantiation fails, use class name
        _tool_registry[tool_class.__name__.lower()] = tool_class
    return tool_class


def get_tool_registry() -> dict[str, Type[BaseTool]]:
    """Get all registered tools."""
    return _tool_registry.copy()


# ============================================================================
# Obsidian Tools
# ============================================================================

class ObsidianReadInput(BaseModel):
    """Input for reading Obsidian files."""

    path: str = Field(..., description="Path relative to cm-workflow/")
    include_frontmatter: bool = Field(True, description="Include YAML frontmatter")


@register_tool
class ObsidianTool(BaseTool):
    """Tool for interacting with Obsidian vault (cm-workflow/)."""

    name: str = "obsidian"
    description: str = """Interact with the Obsidian workflow vault (cm-workflow/).
    
Use this tool to:
- Read task files from backlog/ or sprints/
- Create new tasks in backlog/
- Update task status
- Read plans and reviews
- Create new plans

Input should be a JSON object with 'action' and 'params'.
Actions: read, write, update_status, list_tasks, create_task
"""
    args_schema: Type[BaseModel] = ObsidianReadInput
    vault_path: str = "cm-workflow"

    def _run(self, path: str, include_frontmatter: bool = True) -> str:
        """Read an Obsidian file."""
        try:
            import os

            full_path = os.path.join(self.vault_path, path)
            if not os.path.exists(full_path):
                raise ToolException(f"File not found: {path}")

            with open(full_path, "r") as f:
                content = f.read()

            if not include_frontmatter and content.startswith("---"):
                # Remove frontmatter
                end = content.find("---", 3)
                if end != -1:
                    content = content[end + 3:].strip()

            return content
        except Exception as e:
            raise ToolException(f"Failed to read Obsidian file: {e}")

    async def _arun(self, path: str, include_frontmatter: bool = True) -> str:
        """Async read an Obsidian file."""
        return self._run(path, include_frontmatter)


class ObsidianWriteInput(BaseModel):
    """Input for writing Obsidian files."""

    path: str = Field(..., description="Path relative to cm-workflow/")
    content: str = Field(..., description="File content (Markdown)")
    overwrite: bool = Field(False, description="Overwrite if exists")


class ObsidianWriteTool(BaseTool):
    """Tool for writing to Obsidian vault."""

    name: str = "obsidian_write"
    description: str = """Write a file to the Obsidian workflow vault.
    
Use for creating:
- Tasks in backlog/
- Sprint plans in sprints/
- Reviews in reviews/
- Plans in plans/

Always include proper frontmatter with status, tracking, etc.
"""
    args_schema: Type[BaseModel] = ObsidianWriteInput
    vault_path: str = "cm-workflow"

    def _run(self, path: str, content: str, overwrite: bool = False) -> str:
        """Write an Obsidian file."""
        try:
            import os

            full_path = os.path.join(self.vault_path, path)
            if os.path.exists(full_path) and not overwrite:
                raise ToolException(f"File exists: {path}. Set overwrite=True to replace.")

            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)

            return f"Successfully wrote: {path}"
        except Exception as e:
            raise ToolException(f"Failed to write Obsidian file: {e}")

    async def _arun(self, path: str, content: str, overwrite: bool = False) -> str:
        """Async write an Obsidian file."""
        return self._run(path, content, overwrite)


# ============================================================================
# GitHub MCP Tools
# ============================================================================

class GitHubIssueInput(BaseModel):
    """Input for GitHub issue operations."""

    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    issue_number: Optional[int] = Field(None, description="Issue number for read/update")
    title: Optional[str] = Field(None, description="Issue title for create")
    body: Optional[str] = Field(None, description="Issue body")
    labels: list[str] = Field(default_factory=list, description="Issue labels")


@register_tool
class GitHubMCPTool(BaseTool):
    """Tool for GitHub MCP operations."""

    name: str = "github_mcp"
    description: str = """Interact with GitHub via MCP server.
    
Use this tool to:
- Create tracking issues
- Update issue status
- Create pull requests
- Add comments to PRs
- Search for issues

This tool wraps the GitHub MCP server for seamless integration.
"""
    args_schema: Type[BaseModel] = GitHubIssueInput

    def _run(
        self,
        owner: str,
        repo: str,
        issue_number: Optional[int] = None,
        title: Optional[str] = None,
        body: Optional[str] = None,
        labels: Optional[list[str]] = None,
    ) -> str:
        """Execute GitHub operation."""
        # This would integrate with the actual MCP server
        # For now, return placeholder
        if issue_number:
            return f"Would read issue #{issue_number} from {owner}/{repo}"
        elif title:
            return f"Would create issue '{title}' in {owner}/{repo}"
        else:
            return f"GitHub operation on {owner}/{repo}"

    async def _arun(
        self,
        owner: str,
        repo: str,
        issue_number: Optional[int] = None,
        title: Optional[str] = None,
        body: Optional[str] = None,
        labels: Optional[list[str]] = None,
    ) -> str:
        """Async GitHub operation."""
        return self._run(owner, repo, issue_number, title, body, labels)


# ============================================================================
# Serena Tools
# ============================================================================

class SerenaSymbolInput(BaseModel):
    """Input for Serena symbol operations."""

    symbol_name: str = Field(..., description="Symbol name to find")
    file_path: Optional[str] = Field(None, description="File path to search in")
    include_body: bool = Field(False, description="Include symbol body")


@register_tool
class SerenaTool(BaseTool):
    """Tool for Serena code analysis operations."""

    name: str = "serena"
    description: str = """Interact with Serena for code analysis.
    
Use this tool to:
- Find symbols (functions, classes, methods)
- Get symbol references
- Read file contents
- Analyze code structure

Serena provides semantic understanding of the codebase.
"""
    args_schema: Type[BaseModel] = SerenaSymbolInput

    def _run(
        self,
        symbol_name: str,
        file_path: Optional[str] = None,
        include_body: bool = False,
    ) -> str:
        """Find symbol in codebase."""
        # This would integrate with Serena MCP
        result = f"Finding symbol '{symbol_name}'"
        if file_path:
            result += f" in {file_path}"
        if include_body:
            result += " (with body)"
        return result

    async def _arun(
        self,
        symbol_name: str,
        file_path: Optional[str] = None,
        include_body: bool = False,
    ) -> str:
        """Async find symbol."""
        return self._run(symbol_name, file_path, include_body)


# ============================================================================
# File System Tools
# ============================================================================

class FileReadInput(BaseModel):
    """Input for file read operations."""

    path: str = Field(..., description="File path")
    start_line: Optional[int] = Field(None, description="Start line (1-indexed)")
    end_line: Optional[int] = Field(None, description="End line (1-indexed)")


class FileReadTool(BaseTool):
    """Tool for reading files."""

    name: str = "file_read"
    description: str = """Read file contents.
    
Use for reading:
- Source code files
- Configuration files
- Documentation

Supports line range selection for large files.
"""
    args_schema: Type[BaseModel] = FileReadInput

    def _run(
        self,
        path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
    ) -> str:
        """Read file contents."""
        try:
            with open(path, "r") as f:
                lines = f.readlines()

            if start_line is not None and end_line is not None:
                lines = lines[start_line - 1 : end_line]

            return "".join(lines)
        except Exception as e:
            raise ToolException(f"Failed to read file: {e}")

    async def _arun(
        self,
        path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
    ) -> str:
        """Async read file."""
        return self._run(path, start_line, end_line)


class FileWriteInput(BaseModel):
    """Input for file write operations."""

    path: str = Field(..., description="File path")
    content: str = Field(..., description="File content")
    create_dirs: bool = Field(True, description="Create parent directories")


class FileWriteTool(BaseTool):
    """Tool for writing files."""

    name: str = "file_write"
    description: str = """Write file contents.
    
Use for creating:
- Source code files
- Configuration files
- Documentation

Will create parent directories if needed.
"""
    args_schema: Type[BaseModel] = FileWriteInput

    def _run(
        self,
        path: str,
        content: str,
        create_dirs: bool = True,
    ) -> str:
        """Write file contents."""
        try:
            import os

            if create_dirs:
                os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, "w") as f:
                f.write(content)

            return f"Successfully wrote: {path}"
        except Exception as e:
            raise ToolException(f"Failed to write file: {e}")

    async def _arun(
        self,
        path: str,
        content: str,
        create_dirs: bool = True,
    ) -> str:
        """Async write file."""
        return self._run(path, content, create_dirs)


# ============================================================================
# Tool Factory
# ============================================================================

def create_tools(
    include_obsidian: bool = True,
    include_github: bool = True,
    include_serena: bool = True,
    include_file: bool = True,
    vault_path: str = "cm-workflow",
) -> list[BaseTool]:
    """Create a list of tools for an agent.

    Args:
        include_obsidian: Include Obsidian tools
        include_github: Include GitHub MCP tools
        include_serena: Include Serena tools
        include_file: Include file system tools
        vault_path: Path to Obsidian vault

    Returns:
        List of configured tools
    """
    tools = []

    if include_obsidian:
        obsidian_read = ObsidianTool()
        obsidian_read.vault_path = vault_path
        tools.append(obsidian_read)
        
        obsidian_write = ObsidianWriteTool()
        obsidian_write.vault_path = vault_path
        tools.append(obsidian_write)

    if include_github:
        tools.append(GitHubMCPTool())

    if include_serena:
        tools.append(SerenaTool())

    if include_file:
        tools.append(FileReadTool())
        tools.append(FileWriteTool())

    return tools
