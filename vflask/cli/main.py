"""Command line interface for vflask."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import click

from vflask.core.scaffolder import ModuleScaffolder, ProjectScaffolder, parse_field_spec


@click.group()
def cli() -> None:
    """Create typed Flask projects and modules."""


@cli.command("new")
@click.argument("project_name")
@click.option("--path", "destination", default=".", show_default=True, help="Directory to generate the project into.")
def new_project(project_name: str, destination: str) -> None:
    """Create a new project scaffold."""
    root = Path(destination)
    project_dir = ProjectScaffolder.render_project(project_name, root)
    click.echo(f"✅ Created project '{project_name}' in {project_dir}")


@cli.group("module")
def module_group() -> None:
    """Module-related commands."""


@module_group.command("create")
@click.argument("module_name")
@click.option("-f", "--field", "fields", multiple=True, help="Field definition as name:type[:flag]. Example: name:string:index")
@click.option("-r", "--role", "roles", multiple=True, default=("admin",), show_default=True, help="Roles allowed to access the module.")
@click.option("-m", "--mode", "crud_mode", type=click.Choice(["c", "cr", "crd", "crud"], case_sensitive=False), default="crud", show_default=True, help="CRUD generation mode shorthand: c, cr, crd, or crud.")
@click.option("--project-root", default=".", show_default=True, help="Root of the generated project.")
def create_module(module_name: str, fields: tuple[str, ...], roles: tuple[str, ...], crud_mode: str, project_root: str) -> None:
    """Create a Flask module inside an existing project."""
    project_dir = Path(project_root).resolve()
    parsed_fields = [parse_field_spec(spec) for spec in fields]
    ModuleScaffolder.create_module(project_dir, module_name, parsed_fields, list(roles), crud_mode=crud_mode.lower())
    click.echo(f"✅ Created module '{module_name}' in {project_dir / 'app' / 'modules'}")


@cli.command("watch")
@click.option("--project-root", default=".", show_default=True, help="Project root to watch.")
def watch(project_root: str) -> None:
    """Start the project watcher for module docs auto-generation."""
    from vflask.core.watcher import start_watcher

    start_watcher(Path(project_root).resolve())


@cli.command("run")
@click.option("--project-root", default=".", show_default=True, help="Root of the generated project.")
@click.option("--host", default="127.0.0.1", show_default=True, help="Interface for the development server.")
@click.option("--port", default=5000, type=click.IntRange(1, 65535), show_default=True)
@click.option("--with-services/--no-services", default=True, show_default=True, help="Start local Postgres and Redis with Docker Compose.")
def run_project(project_root: str, host: str, port: int, with_services: bool) -> None:
    """Prepare the database and run a generated Flask application."""
    root = Path(project_root).expanduser().resolve()
    if not (root / "app" / "__init__.py").is_file():
        raise click.ClickException(f"No generated Flask app found under {root}")

    env_file = root / ".env"
    env_example = root / ".env.example"
    if not env_file.exists() and env_example.is_file():
        shutil.copyfile(env_example, env_file)

    environment = os.environ.copy()
    environment["APP_ENV"] = "development"
    environment["FLASK_DEBUG"] = "1"
    environment["PYTHONPATH"] = str(root)

    if with_services:
        if not (root / "docker-compose.yml").is_file():
            raise click.ClickException("docker-compose.yml not found; use --no-services with an external database")
        _run_project_command(["docker", "compose", "up", "-d", "--wait", "db", "redis"], root, environment)
        _wait_for_postgres(root, environment)

    revisions_dir = root / "migrations" / "versions"
    if any(path.suffix == ".py" and path.name != "__init__.py" for path in revisions_dir.glob("*.py")):
        _run_project_command([sys.executable, "-m", "flask", "--app", "app:create_app", "db", "upgrade"], root, environment)
    _run_project_command([sys.executable, "-m", "app.cli", "init-db"], root, environment)
    click.echo(f"Starting Flask at http://{host}:{port}")
    _run_project_command(
        [sys.executable, "-m", "flask", "--app", "app:create_app", "run", "--debug", "--host", host, "--port", str(port)],
        root,
        environment,
    )


def _run_project_command(command: list[str], root: Path, environment: dict[str, str]) -> None:
    try:
        subprocess.run(command, cwd=root, env=environment, check=True)
    except FileNotFoundError as error:
        raise click.ClickException(f"Required executable not found: {command[0]}") from error
    except subprocess.CalledProcessError as error:
        raise click.ClickException(f"Command failed with exit code {error.returncode}: {' '.join(command)}") from error


def _wait_for_postgres(root: Path, environment: dict[str, str]) -> None:
    probe = ["docker", "compose", "exec", "-T", "db", "pg_isready", "-U", "app", "-d", "app"]
    for _ in range(30):
        if subprocess.run(probe, cwd=root, env=environment, check=False, capture_output=True).returncode == 0:
            return
        time.sleep(1)
    raise click.ClickException("PostgreSQL did not become ready within 30 seconds")


if __name__ == "__main__":
    cli()
