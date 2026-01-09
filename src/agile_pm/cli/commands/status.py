"""Status CLI command."""
import click
import asyncio

@click.command()
def status():
    """Show system status."""
    click.echo("Agile-PM Status")
    click.echo("=" * 40)
    
    # Check database
    try:
        from agile_pm.storage.health import check_database
        db_ok = asyncio.run(check_database())
        click.echo(f"Database: {'✓ Connected' if db_ok else '✗ Disconnected'}")
    except Exception:
        click.echo("Database: ✗ Not configured")
    
    # Check Redis
    try:
        from agile_pm.storage.health import check_redis
        redis_ok = asyncio.run(check_redis())
        click.echo(f"Redis: {'✓ Connected' if redis_ok else '✗ Disconnected'}")
    except Exception:
        click.echo("Redis: ✗ Not configured")
    
    click.echo("=" * 40)
