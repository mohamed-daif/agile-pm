"""Main CLI entry point for Agile-PM."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

app = typer.Typer(
    name="agile-pm",
    help="AI-powered Agile project management agent framework",
    add_completion=False,
)


@app.command()
def init(
    path: Annotated[Optional[Path], typer.Argument(help="Project path")] = None,
    name: Annotated[str, typer.Option("--name", "-n", help="Project name")] = "my-project",
    project_type: Annotated[str, typer.Option("--type", "-t", help="Project type")] = "python",
) -> None:
    """Initialize Agile-PM in a project."""
    from agile_pm.core.project import AgileProject
    from agile_pm.core.config import ProjectInfo
    
    path = path or Path.cwd()
    typer.echo(f"Initializing Agile-PM in {path}...")
    
    project = AgileProject.init(
        root_path=path,
        project=ProjectInfo(name=name, type=project_type),
    )
    
    typer.echo("✓ Created .agile-pm/")
    typer.echo("✓ Created config.yaml")
    typer.echo("")
    typer.echo("Next steps:")
    typer.echo("  1. Edit .agile-pm/config.yaml to configure your providers")
    typer.echo("  2. Run 'agile-pm link github_copilot' to link a provider")
    typer.echo("  3. Run 'agile-pm sync' to sync configurations")


@app.command()
def link(
    provider: Annotated[str, typer.Argument(help="Provider name (github_copilot, qodo, cursor, codex)")],
    config: Annotated[Optional[Path], typer.Option("--config", "-c", help="Config file path")] = None,
) -> None:
    """Link Agile-PM to an AI provider."""
    from agile_pm.core.project import AgileProject
    
    config_path = config or Path(".agile-pm/config.yaml")
    project = AgileProject.from_config(config_path)
    
    typer.echo(f"Linking to {provider}...")
    project.link_provider(provider)
    typer.echo(f"✓ Linked to {provider}")


@app.command()
def sync(
    config: Annotated[Optional[Path], typer.Option("--config", "-c", help="Config file path")] = None,
) -> None:
    """Sync all provider configurations."""
    from agile_pm.core.project import AgileProject
    
    config_path = config or Path(".agile-pm/config.yaml")
    project = AgileProject.from_config(config_path)
    
    typer.echo("Syncing provider configurations...")
    project.sync()
    typer.echo("✓ All providers synced")


@app.command()
def uninstall(
    keep_overrides: Annotated[bool, typer.Option("--keep-overrides", "-k", help="Keep custom overrides")] = False,
    config: Annotated[Optional[Path], typer.Option("--config", "-c", help="Config file path")] = None,
) -> None:
    """Remove Agile-PM from the project."""
    from agile_pm.core.project import AgileProject
    
    config_path = config or Path(".agile-pm/config.yaml")
    project = AgileProject.from_config(config_path)
    
    typer.echo("Removing Agile-PM...")
    project.uninstall(keep_overrides=keep_overrides)
    typer.echo("✓ Agile-PM removed")
    
    if keep_overrides:
        typer.echo("  (Overrides backed up to .agile-pm-overrides-backup)")


@app.command()
def dashboard(
    host: Annotated[str, typer.Option("--host", "-h", help="Host to bind to")] = "127.0.0.1",
    port: Annotated[int, typer.Option("--port", "-p", help="Port to bind to")] = 8080,
    config: Annotated[Optional[Path], typer.Option("--config", "-c", help="Config file path")] = None,
) -> None:
    """Start the Agile-PM dashboard."""
    from agile_pm.core.project import AgileProject
    
    config_path = config or Path(".agile-pm/config.yaml")
    project = AgileProject.from_config(config_path)
    
    typer.echo(f"Starting dashboard at http://{host}:{port}...")
    project.dashboard.start(host=host, port=port)


@app.command()
def version() -> None:
    """Show Agile-PM version."""
    from agile_pm import __version__
    typer.echo(f"Agile-PM v{__version__}")


def main() -> None:
    """Main entry point."""
    app()


# Alias for CLI entry point
cli = main


if __name__ == "__main__":
    main()
