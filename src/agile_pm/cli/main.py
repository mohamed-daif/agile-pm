"""Main CLI entry point for Agile PM Agents."""

import asyncio
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(
    name="agile-pm",
    help="AI-powered Agile Project Management Agents",
    no_args_is_help=True,
)

console = Console()


# Import and register command groups
from .commands import crew, memory, trace, config

app.add_typer(crew.app, name="crew", help="Manage agent crews")
app.add_typer(memory.app, name="memory", help="Manage agent memory")
app.add_typer(trace.app, name="trace", help="View traces and spans")
app.add_typer(config.app, name="config", help="Configuration management")


@app.command()
def version():
    """Show version information."""
    console.print(Panel.fit(
        "[bold blue]Agile PM Agents[/bold blue]\n"
        "Version: 1.0.0\n"
        "Python: " + sys.version.split()[0],
        title="Version Info",
    ))


@app.command()
def status():
    """Show system status."""
    from ..dashboard.metrics import MetricsCollector
    
    collector = MetricsCollector()
    metrics = collector.get_system_metrics()
    
    table = Table(title="System Status")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Active Agents", str(metrics.active_agents))
    table.add_row("Idle Agents", str(metrics.idle_agents))
    table.add_row("Tasks Queued", str(metrics.tasks_queued))
    table.add_row("Tasks In Progress", str(metrics.tasks_in_progress))
    table.add_row("Completed (1h)", str(metrics.tasks_completed_last_hour))
    table.add_row("Success Rate", f"{metrics.success_rate:.1%}")
    table.add_row("Avg Duration", f"{metrics.avg_task_duration:.2f}s")
    
    console.print(table)


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),
    port: int = typer.Option(8080, help="Port to listen on"),
    workers: int = typer.Option(4, help="Number of workers"),
    reload: bool = typer.Option(False, help="Enable auto-reload"),
):
    """Start the API server."""
    console.print(f"[bold green]Starting server on {host}:{port}...[/bold green]")
    
    try:
        import uvicorn
        uvicorn.run(
            "agile_pm.api:app",
            host=host,
            port=port,
            workers=workers,
            reload=reload,
        )
    except ImportError:
        console.print("[red]uvicorn not installed. Run: pip install uvicorn[/red]")
        raise typer.Exit(1)


@app.command()
def dashboard(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),
    port: int = typer.Option(8765, help="WebSocket port"),
):
    """Start the real-time dashboard server."""
    from ..dashboard.server import run_dashboard_server
    
    console.print(f"[bold green]Starting dashboard on ws://{host}:{port}...[/bold green]")
    
    async def run():
        server = await run_dashboard_server(host=host, port=port)
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await server.stop()
    
    asyncio.run(run())


@app.command()
def run_task(
    task_id: str = typer.Argument(..., help="Task ID to execute"),
    agent: str = typer.Option("auto", help="Agent to assign"),
    dry_run: bool = typer.Option(False, help="Show what would happen"),
):
    """Execute a single task."""
    console.print(f"[bold]Running task: {task_id}[/bold]")
    
    if dry_run:
        console.print("[yellow]Dry run - no changes will be made[/yellow]")
        return
    
    # TODO: Implement task execution
    console.print(f"[green]Task {task_id} completed[/green]")


@app.command()
def plan(
    goal: str = typer.Argument(..., help="Sprint goal"),
    capacity: int = typer.Option(50, help="Team capacity in story points"),
    duration: str = typer.Option("2 weeks", help="Sprint duration"),
    output: Optional[str] = typer.Option(None, help="Output file path"),
):
    """Create a sprint plan using the Planning Crew."""
    from ..crews import PlanningCrew
    from ..crews.planning_crew import SprintPlanInput
    
    console.print(f"[bold blue]Creating sprint plan...[/bold blue]")
    console.print(f"Goal: {goal}")
    console.print(f"Capacity: {capacity} points")
    
    crew = PlanningCrew()
    input_data = SprintPlanInput(
        sprint_goal=goal,
        backlog_items=[],  # Would load from Obsidian
        team_capacity=capacity,
        sprint_duration=duration,
    )
    
    result = crew.kickoff(input_data)
    
    if result.success:
        console.print("[green]Sprint plan created successfully![/green]")
        console.print(result.output)
        
        if output:
            with open(output, "w") as f:
                f.write(str(result.output))
            console.print(f"[dim]Saved to {output}[/dim]")
    else:
        console.print(f"[red]Planning failed: {result.output}[/red]")
        raise typer.Exit(1)


@app.command()
def review(
    path: str = typer.Argument(..., help="File or PR to review"),
    type: str = typer.Option("code", help="Review type: code, security, performance"),
    output: Optional[str] = typer.Option(None, help="Output file path"),
):
    """Run code review using the Review Crew."""
    from ..crews import ReviewCrew
    from ..crews.review_crew import ReviewInput, ReviewType
    
    console.print(f"[bold blue]Running {type} review...[/bold blue]")
    
    review_type = ReviewType(type)
    
    crew = ReviewCrew()
    input_data = ReviewInput(
        title=f"Review of {path}",
        description="Automated code review",
        review_type=review_type,
        files_changed=[{"path": path, "status": "modified"}],
    )
    
    result = crew.kickoff(input_data)
    
    if result.success:
        console.print("[green]Review completed![/green]")
        console.print(result.output)
        
        if output:
            with open(output, "w") as f:
                f.write(str(result.output))
    else:
        console.print(f"[red]Review failed: {result.output}[/red]")


@app.callback()
def main_callback(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
):
    """Agile PM Agents - AI-powered project management."""
    if debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    elif verbose:
        import logging
        logging.basicConfig(level=logging.INFO)


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
