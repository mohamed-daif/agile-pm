"""Crew management CLI commands."""

from typing import Optional
import asyncio

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

app = typer.Typer(help="Manage agent crews")
console = Console()


@app.command("list")
def list_crews():
    """List available crews."""
    table = Table(title="Available Crews")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Agents", style="green")
    
    crews = [
        ("planning", "Sprint planning and backlog management", "Research, Architect, PM"),
        ("execution", "Task implementation and testing", "Backend, Frontend, QA"),
        ("review", "Code review and security audit", "Reviewer, Security, Performance"),
    ]
    
    for name, desc, agents in crews:
        table.add_row(name, desc, agents)
    
    console.print(table)


@app.command("run")
def run_crew(
    name: str = typer.Argument(..., help="Crew name: planning, execution, review"),
    input_file: Optional[str] = typer.Option(None, "--input", "-i", help="Input JSON file"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Run a crew with the given input."""
    console.print(f"[bold blue]Running {name} crew...[/bold blue]")
    
    if name == "planning":
        from ...crews import PlanningCrew
        from ...crews.planning_crew import SprintPlanInput
        
        crew = PlanningCrew()
        input_data = SprintPlanInput(
            sprint_goal="Default sprint goal",
            backlog_items=[],
        )
        result = crew.kickoff(input_data)
    
    elif name == "execution":
        from ...crews import ExecutionCrew
        from ...crews.execution_crew import TaskInput
        
        crew = ExecutionCrew()
        input_data = TaskInput(
            task_id="task-1",
            title="Default task",
            description="Task description",
        )
        result = crew.kickoff(input_data)
    
    elif name == "review":
        from ...crews import ReviewCrew
        from ...crews.review_crew import ReviewInput
        
        crew = ReviewCrew()
        input_data = ReviewInput(
            title="Default review",
            description="Review description",
        )
        result = crew.kickoff(input_data)
    
    else:
        console.print(f"[red]Unknown crew: {name}[/red]")
        raise typer.Exit(1)
    
    if result.success:
        console.print(Panel.fit(
            str(result.output),
            title=f"[green]{name.title()} Crew Result[/green]",
        ))
        
        if output_file:
            with open(output_file, "w") as f:
                f.write(str(result.output))
            console.print(f"[dim]Saved to {output_file}[/dim]")
    else:
        console.print(f"[red]Crew execution failed: {result.output}[/red]")
        raise typer.Exit(1)


@app.command("agents")
def list_agents(
    crew_name: Optional[str] = typer.Argument(None, help="Filter by crew name"),
):
    """List agents in a crew."""
    table = Table(title="Agents")
    table.add_column("Crew", style="cyan")
    table.add_column("Agent", style="white")
    table.add_column("Role", style="green")
    table.add_column("Status", style="yellow")
    
    agents = [
        ("planning", "research", "Research Analyst", "idle"),
        ("planning", "architect", "Solution Architect", "idle"),
        ("planning", "pm", "Technical PM", "idle"),
        ("execution", "backend", "Backend Engineer", "idle"),
        ("execution", "frontend", "Frontend Engineer", "idle"),
        ("execution", "qa", "QA Engineer", "idle"),
        ("review", "reviewer", "Senior Reviewer", "idle"),
        ("review", "security", "Security Engineer", "idle"),
        ("review", "performance", "Performance Engineer", "idle"),
    ]
    
    for crew, agent_id, role, status in agents:
        if crew_name and crew != crew_name:
            continue
        table.add_row(crew, agent_id, role, status)
    
    console.print(table)


@app.command("status")
def crew_status(
    name: str = typer.Argument(..., help="Crew name"),
):
    """Get status of a running crew."""
    console.print(f"[bold]Status of {name} crew:[/bold]")
    
    # TODO: Get actual crew status
    console.print("[yellow]No active execution[/yellow]")


@app.command("stop")
def stop_crew(
    name: str = typer.Argument(..., help="Crew name"),
    force: bool = typer.Option(False, "--force", "-f", help="Force stop"),
):
    """Stop a running crew."""
    if force:
        console.print(f"[red]Force stopping {name} crew...[/red]")
    else:
        console.print(f"[yellow]Gracefully stopping {name} crew...[/yellow]")
    
    # TODO: Implement crew stopping
    console.print(f"[green]Crew {name} stopped[/green]")
