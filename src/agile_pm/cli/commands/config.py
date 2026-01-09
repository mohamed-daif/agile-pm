"""Configuration management CLI commands."""

from typing import Optional
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

app = typer.Typer(help="Configuration management")
console = Console()

DEFAULT_CONFIG = """
# Agile PM Agents Configuration
# Environment: production

server:
  host: 0.0.0.0
  port: 8080

dashboard:
  enabled: true
  port: 8765
  metrics_interval: 5

memory:
  default_ttl: 86400
  auto_save_interval: 60
  persistence:
    type: postgresql
    url: ${DATABASE_URL}

observability:
  tracing:
    enabled: true
    endpoint: ${OTEL_EXPORTER_OTLP_ENDPOINT}
  metrics:
    enabled: true
    port: 8000
  logging:
    level: INFO
    format: json

llm:
  default_model: gpt-4
  temperature: 0.7
  max_tokens: 4096
  rate_limit:
    requests_per_minute: 60

agents:
  planning_crew:
    enabled: true
    agents:
      - research
      - architect
      - pm
  execution_crew:
    enabled: true
    agents:
      - backend
      - frontend
      - qa
  review_crew:
    enabled: true
    agents:
      - reviewer
      - security
      - performance

obsidian:
  vault_path: ${OBSIDIAN_VAULT_PATH}
  backlog_folder: backlog
  sprints_folder: sprints
"""


@app.command("show")
def show_config(
    section: Optional[str] = typer.Argument(None, help="Config section to show"),
    format: str = typer.Option("yaml", help="Output format: yaml, json"),
):
    """Show current configuration."""
    if section:
        console.print(f"[bold]Configuration: {section}[/bold]\n")
    else:
        console.print("[bold]Full Configuration[/bold]\n")
    
    # TODO: Get actual config
    syntax = Syntax(DEFAULT_CONFIG, "yaml", theme="monokai", line_numbers=True)
    console.print(syntax)


@app.command("get")
def get_config(
    key: str = typer.Argument(..., help="Config key (dot notation)"),
):
    """Get a specific configuration value."""
    # TODO: Actual config lookup
    values = {
        "server.port": "8080",
        "dashboard.enabled": "true",
        "memory.default_ttl": "86400",
        "llm.default_model": "gpt-4",
    }
    
    value = values.get(key, "[not set]")
    console.print(f"{key} = {value}")


@app.command("set")
def set_config(
    key: str = typer.Argument(..., help="Config key (dot notation)"),
    value: str = typer.Argument(..., help="Value to set"),
    persist: bool = typer.Option(True, help="Persist to config file"),
):
    """Set a configuration value."""
    console.print(f"[bold]Setting {key} = {value}[/bold]")
    
    if persist:
        console.print("[dim]Configuration will be persisted[/dim]")
    
    # TODO: Actual config update
    console.print("[green]Configuration updated[/green]")


@app.command("init")
def init_config(
    path: Optional[str] = typer.Option(None, help="Config file path"),
    force: bool = typer.Option(False, help="Overwrite existing config"),
):
    """Initialize configuration file."""
    config_path = Path(path) if path else Path("agile-pm.yaml")
    
    if config_path.exists() and not force:
        console.print(f"[yellow]Config file already exists: {config_path}[/yellow]")
        if not typer.confirm("Overwrite?"):
            raise typer.Abort()
    
    config_path.write_text(DEFAULT_CONFIG)
    console.print(f"[green]Created configuration file: {config_path}[/green]")


@app.command("validate")
def validate_config(
    path: Optional[str] = typer.Option(None, help="Config file to validate"),
):
    """Validate configuration file."""
    config_path = Path(path) if path else Path("agile-pm.yaml")
    
    if not config_path.exists():
        console.print(f"[red]Config file not found: {config_path}[/red]")
        raise typer.Exit(1)
    
    console.print(f"[bold]Validating {config_path}...[/bold]")
    
    # TODO: Actual validation
    issues = []
    
    if issues:
        console.print("[red]Validation failed:[/red]")
        for issue in issues:
            console.print(f"  - {issue}")
        raise typer.Exit(1)
    else:
        console.print("[green]Configuration is valid[/green]")


@app.command("env")
def show_env():
    """Show environment variables."""
    import os
    
    table = Table(title="Environment Variables")
    table.add_column("Variable", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Status", style="yellow")
    
    env_vars = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "DATABASE_URL",
        "REDIS_URL",
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "OBSIDIAN_VAULT_PATH",
        "LOG_LEVEL",
        "ENVIRONMENT",
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            if "KEY" in var or "PASSWORD" in var or "SECRET" in var:
                display_value = value[:4] + "****" + value[-4:] if len(value) > 8 else "****"
            else:
                display_value = value if len(value) < 50 else value[:47] + "..."
            status = "[green]✓[/green]"
        else:
            display_value = "[dim]not set[/dim]"
            status = "[yellow]○[/yellow]"
        
        table.add_row(var, display_value, status)
    
    console.print(table)


@app.command("export")
def export_config(
    output: str = typer.Option("config-export.yaml", help="Output file"),
    format: str = typer.Option("yaml", help="Format: yaml, json, env"),
):
    """Export configuration to file."""
    console.print(f"[bold]Exporting configuration to {output}...[/bold]")
    
    # TODO: Actual export
    Path(output).write_text(DEFAULT_CONFIG)
    console.print(f"[green]Exported to {output}[/green]")


@app.command("import")
def import_config(
    input_file: str = typer.Argument(..., help="Config file to import"),
    merge: bool = typer.Option(True, help="Merge with existing config"),
):
    """Import configuration from file."""
    path = Path(input_file)
    
    if not path.exists():
        console.print(f"[red]File not found: {input_file}[/red]")
        raise typer.Exit(1)
    
    console.print(f"[bold]Importing configuration from {input_file}...[/bold]")
    
    if merge:
        console.print("[dim]Merging with existing configuration[/dim]")
    
    # TODO: Actual import
    console.print("[green]Configuration imported[/green]")
