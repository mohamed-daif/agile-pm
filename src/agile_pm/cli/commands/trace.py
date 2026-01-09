"""Trace viewing CLI commands."""

from typing import Optional
from datetime import datetime, timedelta

import typer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel

app = typer.Typer(help="View traces and spans")
console = Console()


@app.command("list")
def list_traces(
    service: Optional[str] = typer.Option(None, help="Filter by service"),
    status: Optional[str] = typer.Option(None, help="Filter by status: ok, error"),
    limit: int = typer.Option(20, help="Maximum traces to show"),
    since: str = typer.Option("1h", help="Time range: 1h, 24h, 7d"),
):
    """List recent traces."""
    table = Table(title=f"Recent Traces (last {since})")
    table.add_column("Trace ID", style="cyan", no_wrap=True)
    table.add_column("Service", style="white")
    table.add_column("Operation", style="yellow")
    table.add_column("Duration", style="green")
    table.add_column("Status", style="red")
    table.add_column("Time", style="dim")
    
    # TODO: Get actual traces from OpenTelemetry backend
    traces = [
        ("abc123def456", "agile-pm-agents", "crew.planning", "2.5s", "OK", "10:30"),
        ("789xyz012abc", "agile-pm-agents", "task.execute", "45.2s", "OK", "10:25"),
        ("456def789ghi", "agile-pm-agents", "llm.call", "1.2s", "ERROR", "10:20"),
    ]
    
    for row in traces[:limit]:
        if service and row[1] != service:
            continue
        if status and row[4].lower() != status.lower():
            continue
        
        status_style = "green" if row[4] == "OK" else "red"
        table.add_row(
            row[0][:12] + "...",
            row[1],
            row[2],
            row[3],
            f"[{status_style}]{row[4]}[/{status_style}]",
            row[5],
        )
    
    console.print(table)


@app.command("show")
def show_trace(
    trace_id: str = typer.Argument(..., help="Trace ID to show"),
    raw: bool = typer.Option(False, help="Show raw JSON"),
):
    """Show trace details."""
    console.print(f"[bold]Trace: {trace_id}[/bold]\n")
    
    # Build trace tree
    tree = Tree(f"[bold cyan]Trace {trace_id[:12]}...[/bold cyan]")
    
    # TODO: Get actual trace data
    root = tree.add("[green]crew.planning (2.5s)")
    research = root.add("[green]task.research (0.8s)")
    research.add("[green]llm.call (0.5s)")
    research.add("[green]memory.retrieve (0.1s)")
    
    architect = root.add("[green]task.architect (0.9s)")
    architect.add("[green]llm.call (0.7s)")
    
    pm = root.add("[green]task.planning (0.8s)")
    pm.add("[green]llm.call (0.6s)")
    pm.add("[green]memory.save (0.05s)")
    
    console.print(tree)
    
    if raw:
        console.print("\n[dim]Raw JSON would be displayed here[/dim]")


@app.command("spans")
def list_spans(
    trace_id: str = typer.Argument(..., help="Trace ID"),
    sort: str = typer.Option("start", help="Sort by: start, duration"),
):
    """List spans in a trace."""
    table = Table(title=f"Spans in Trace {trace_id[:12]}...")
    table.add_column("Span ID", style="cyan", no_wrap=True)
    table.add_column("Operation", style="white")
    table.add_column("Duration", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Attributes", style="dim")
    
    # TODO: Get actual spans
    spans = [
        ("span-001", "crew.planning", "2.5s", "OK", "agents=3"),
        ("span-002", "task.research", "0.8s", "OK", ""),
        ("span-003", "llm.call", "0.5s", "OK", "model=gpt-4"),
        ("span-004", "memory.retrieve", "0.1s", "OK", "entries=10"),
        ("span-005", "task.architect", "0.9s", "OK", ""),
        ("span-006", "llm.call", "0.7s", "OK", "model=gpt-4"),
    ]
    
    for row in spans:
        table.add_row(*row)
    
    console.print(table)


@app.command("errors")
def list_errors(
    since: str = typer.Option("24h", help="Time range"),
    limit: int = typer.Option(10, help="Maximum errors to show"),
):
    """List recent errors."""
    table = Table(title=f"Errors (last {since})")
    table.add_column("Time", style="dim")
    table.add_column("Trace ID", style="cyan")
    table.add_column("Operation", style="white")
    table.add_column("Error", style="red")
    
    # TODO: Get actual errors
    errors = [
        ("10:20", "456def789", "llm.call", "RateLimitError: Too many requests"),
        ("09:15", "123abc456", "memory.save", "ConnectionError: Database unavailable"),
    ]
    
    for row in errors[:limit]:
        table.add_row(*row)
    
    console.print(table)


@app.command("stats")
def trace_stats(
    since: str = typer.Option("1h", help="Time range"),
):
    """Show tracing statistics."""
    table = Table(title=f"Trace Statistics (last {since})")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    stats = [
        ("Total Traces", "145"),
        ("Total Spans", "892"),
        ("Error Rate", "2.1%"),
        ("Avg Duration", "1.8s"),
        ("P50 Duration", "1.2s"),
        ("P95 Duration", "5.4s"),
        ("P99 Duration", "12.1s"),
    ]
    
    for name, value in stats:
        table.add_row(name, value)
    
    console.print(table)
    
    # Top operations
    console.print("\n[bold]Top Operations by Count:[/bold]")
    ops_table = Table()
    ops_table.add_column("Operation", style="white")
    ops_table.add_column("Count", style="green")
    ops_table.add_column("Avg Duration", style="yellow")
    
    ops = [
        ("llm.call", "423", "0.9s"),
        ("memory.retrieve", "215", "0.05s"),
        ("task.execute", "89", "15.2s"),
        ("crew.planning", "45", "2.8s"),
    ]
    
    for row in ops:
        ops_table.add_row(*row)
    
    console.print(ops_table)


@app.command("search")
def search_traces(
    query: str = typer.Argument(..., help="Search query"),
    attribute: Optional[str] = typer.Option(None, help="Attribute to search"),
    limit: int = typer.Option(20, help="Maximum results"),
):
    """Search traces by attributes."""
    console.print(f"[bold]Searching for: {query}[/bold]")
    
    if attribute:
        console.print(f"In attribute: {attribute}")
    
    # TODO: Actual search
    console.print("[yellow]No results found[/yellow]")
