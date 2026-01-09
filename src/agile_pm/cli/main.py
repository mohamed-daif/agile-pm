"""Agile-PM CLI main entry point."""
import click
from agile_pm import __version__


@click.group()
@click.version_option(version=__version__)
def app():
    """Agile-PM - AI-Powered Project Management CLI."""
    pass


@app.command()
def version():
    """Show version information."""
    click.echo(f"Agile-PM version {__version__}")


@app.command()
@click.argument("name")
def init(name: str):
    """Initialize a new Agile-PM project.
    
    NAME is the project directory name.
    """
    import os
    os.makedirs(name, exist_ok=True)
    config_path = os.path.join(name, ".agile-pm.yml")
    with open(config_path, "w") as f:
        f.write(f"""# Agile-PM Configuration
version: "1.0"
project:
  name: {name}

agents:
  max_concurrent: 5
  default_timeout: 300

llm:
  provider: openai
  model: gpt-4
  temperature: 0.7
""")
    click.echo(f"✅ Initialized Agile-PM project: {name}")
    click.echo(f"   Config: {config_path}")


# Import and register serve command
from agile_pm.cli.commands.serve import serve
app.add_command(serve)


if __name__ == "__main__":
    app()
