"""Database CLI commands."""
import click
import asyncio

@click.group()
def db():
    """Database management commands."""
    pass

@db.command()
def init():
    """Initialize database tables."""
    from agile_pm.storage.database import init_db
    import os
    
    url = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost/agile_pm")
    database = init_db(url)
    asyncio.run(database.create_tables())
    click.echo("Database tables created.")

@db.command()
def migrate():
    """Run database migrations."""
    import subprocess
    result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
    click.echo(result.stdout)
    if result.returncode != 0:
        click.echo(result.stderr, err=True)

@db.command()
def reset():
    """Reset database (drop and recreate)."""
    if click.confirm("This will delete all data. Continue?"):
        from agile_pm.storage.database import init_db
        import os
        
        url = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost/agile_pm")
        database = init_db(url)
        asyncio.run(database.drop_tables())
        asyncio.run(database.create_tables())
        click.echo("Database reset complete.")
