"""Server command for CLI."""
import click
import uvicorn
import signal
import sys


@click.command()
@click.option("--host", default="0.0.0.0", help="Host to bind")
@click.option("--port", default=8000, type=int, help="Port to bind")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
@click.option("--workers", default=1, type=int, help="Number of workers")
@click.option("--log-level", default="info", help="Log level")
def serve(host: str, port: int, reload: bool, workers: int, log_level: str):
    """Start the Agile-PM API server.
    
    Examples:
    
        # Development with auto-reload
        agile-pm serve --reload
        
        # Production with multiple workers
        agile-pm serve --workers 4
        
        # Custom host and port
        agile-pm serve --host 127.0.0.1 --port 9000
    """
    click.echo(f"🚀 Starting Agile-PM API server...")
    click.echo(f"   Host: {host}")
    click.echo(f"   Port: {port}")
    click.echo(f"   Workers: {workers}")
    click.echo(f"   Reload: {reload}")
    click.echo("")
    click.echo(f"📖 API docs: http://{host}:{port}/docs")
    click.echo(f"❤️  Health: http://{host}:{port}/api/v1/system/health")
    click.echo("")
    
    # Handle graceful shutdown
    def signal_handler(signum, frame):
        click.echo("\n🛑 Shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run server
    uvicorn.run(
        "agile_pm.api.app:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,
        log_level=log_level
    )


if __name__ == "__main__":
    serve()
