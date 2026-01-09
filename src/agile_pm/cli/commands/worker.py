"""Worker CLI command."""
import click
from agile_pm.queue.celery_app import celery_app

@click.command()
@click.option("--concurrency", default=4, help="Number of workers")
@click.option("--queues", default="agents,webhooks,maintenance", help="Queues to consume")
@click.option("--beat", is_flag=True, help="Run with beat scheduler")
@click.option("--loglevel", default="INFO", help="Log level")
def worker(concurrency: int, queues: str, beat: bool, loglevel: str):
    """Start Celery workers."""
    click.echo(f"Starting workers (concurrency={concurrency})...")
    args = ["worker", "-l", loglevel, "-c", str(concurrency), "-Q", queues]
    if beat:
        args.extend(["-B"])
    celery_app.worker_main(args)
