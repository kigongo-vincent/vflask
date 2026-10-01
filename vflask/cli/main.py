"""Command line interface for vflask."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time

import click
from pyfiglet import Figlet

from vflask import __version__
from vflask.core.scaffolder import ModuleScaffolder, ProjectScaffolder, parse_field_spec


@click.version_option(version=__version__, prog_name="vflask")
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
@click.option("-m", "--mode", "crud_mode", type=click.Choice(["c", "cr", "crd", "crud"], case_sensitive=False), default="crud", show_default=True, help="c=create, cr=+read, crd=+delete, crud=+update.")
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


@cli.group("db")
def database_group() -> None:
    """Initialize the database and manage schema migrations."""


@database_group.command("init")
@click.option("--project-root", default=".", show_default=True, help="Root of the generated project.")
def init_database(project_root: str) -> None:
    """Create tables and seed default roles."""
    root = Path(project_root).expanduser().resolve()
    environment = _project_environment(root)
    _run_project_command([sys.executable, "-m", "app.cli", "init-db"], root, environment)


@database_group.command("migrate")
@click.option("-m", "--message", required=True, help="Migration description.")
@click.option("--project-root", default=".", show_default=True, help="Root of the generated project.")
def create_migration(message: str, project_root: str) -> None:
    """Generate a migration from model changes."""
    _run_flask_db_command(project_root, ["migrate", "-m", message])


@database_group.command("upgrade")
@click.option("--project-root", default=".", show_default=True, help="Root of the generated project.")
def upgrade_database(project_root: str) -> None:
    """Apply pending database migrations."""
    _run_flask_db_command(project_root, ["upgrade"])


@database_group.command("downgrade")
@click.option("--revision", default="-1", show_default=True, help="Revision to downgrade to.")
@click.option("--project-root", default=".", show_default=True, help="Root of the generated project.")
def downgrade_database(revision: str, project_root: str) -> None:
    """Roll back to a migration revision."""
    _run_flask_db_command(project_root, ["downgrade", revision])


@database_group.command("current")
@click.option("--project-root", default=".", show_default=True, help="Root of the generated project.")
def current_database_revision(project_root: str) -> None:
    """Show the current database migration revision."""
    _run_flask_db_command(project_root, ["current"])


@cli.command("test", context_settings={"ignore_unknown_options": True})
@click.option("--project-root", default=".", show_default=True, help="Root of the generated project.")
@click.argument("pytest_args", nargs=-1, type=click.UNPROCESSED)
def test_project(project_root: str, pytest_args: tuple[str, ...]) -> None:
    """Run project tests; pass additional pytest options after --."""
    root = Path(project_root).expanduser().resolve()
    environment = _project_environment(root)
    _run_project_command([sys.executable, "-m", "pytest", *pytest_args], root, environment)


@cli.command("app", context_settings={"ignore_unknown_options": True})
@click.option("--project-root", default=".", show_default=True, help="Root of the generated project.")
@click.argument("app_args", nargs=-1, type=click.UNPROCESSED)
def generated_app_command(project_root: str, app_args: tuple[str, ...]) -> None:
    """Run any command provided by the generated app CLI."""
    _run_generated_app_command(project_root, list(app_args))


@cli.command("push")
@click.argument("message", required=False, default="chore: update project")
@click.option("--project-root", default=".", show_default=True, help="Root of the generated project.")
def push_project(message: str, project_root: str) -> None:
    """Commit and push generated project changes."""
    _run_generated_app_command(project_root, ["push", message])


@cli.command("create-user")
@click.argument("email")
@click.argument("name")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option("--project-root", default=".", show_default=True, help="Root of the generated project.")
def create_project_user(email: str, name: str, password: str, project_root: str) -> None:
    """Create an application user."""
    _run_generated_app_command(project_root, ["create-user", email, password, name])


def _run_generated_app_command(project_root: str, arguments: list[str]) -> None:
    root = Path(project_root).expanduser().resolve()
    environment = _project_environment(root)
    _run_project_command([sys.executable, "-m", "app.cli", *arguments], root, environment)


@cli.command("exec", context_settings={"ignore_unknown_options": True})
@click.option("--project-root", default=".", show_default=True, help="Root of the generated project.")
@click.argument("command", nargs=-1, type=click.UNPROCESSED)
def execute_project_command(project_root: str, command: tuple[str, ...]) -> None:
    """Run any executable in the project environment without invoking a shell."""
    if not command:
        raise click.UsageError("Provide a command after --, for example: vflask exec -- python -m pytest -q")
    root = Path(project_root).expanduser().resolve()
    environment = _project_environment(root)
    _run_project_command(list(command), root, environment)


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

    environment = _project_environment(root)
    environment["FLASK_DEBUG"] = "1"

    if with_services:
        if not (root / "docker-compose.yml").is_file():
            raise click.ClickException("docker-compose.yml not found; use --no-services with an external database")
        _run_project_command(["docker", "compose", "up", "-d", "--wait", "db", "redis"], root, environment)
        _wait_for_postgres(root, environment)

    revisions_dir = root / "migrations" / "versions"
    if any(path.suffix == ".py" and path.name != "__init__.py" for path in revisions_dir.glob("*.py")):
        _run_project_command([sys.executable, "-m", "flask", "--app", "app:create_app", "db", "upgrade"], root, environment)
    _run_project_command([sys.executable, "-m", "app.cli", "init-db"], root, environment)
    port = _next_available_port(host, port)
    environment["APP_BASE_URL"] = f"http://{host}:{port}"
    _print_startup_banner()
    click.echo(f"Starting Flask at http://{host}:{port}")
    _run_project_command(
        [sys.executable, "-m", "flask", "--app", "app:create_app", "run", "--debug", "--host", host, "--port", str(port)],
        root,
        environment,
    )


@cli.command("start")
@click.option("--project-root", default=".", show_default=True, help="Root of the generated project.")
@click.option("--host", default="0.0.0.0", show_default=True, help="Interface for the production server.")
@click.option("--port", type=click.IntRange(1, 65535), envvar="PORT", default=5000, show_default=True)
@click.option("--workers", type=click.IntRange(1), envvar="WEB_CONCURRENCY", default=3, show_default=True)
@click.option("--threads", type=click.IntRange(1), envvar="GUNICORN_THREADS", default=2, show_default=True)
@click.option("--timeout", type=click.IntRange(1), envvar="GUNICORN_TIMEOUT", default=60, show_default=True)
def start_project(project_root: str, host: str, port: int, workers: int, threads: int, timeout: int) -> None:
    """Apply migrations and start the production Gunicorn server."""
    root = Path(project_root).expanduser().resolve()
    if not (root / "app" / "__init__.py").is_file():
        raise click.ClickException(f"No generated Flask app found under {root}")

    environment = _project_environment(root)
    environment["APP_ENV"] = "production"
    environment["PORT"] = str(port)
    environment["WEB_CONCURRENCY"] = str(workers)
    environment["GUNICORN_THREADS"] = str(threads)
    environment["GUNICORN_TIMEOUT"] = str(timeout)
    environment.setdefault("APP_BASE_URL", f"http://{host}:{port}")

    revisions_dir = root / "migrations" / "versions"
    if revisions_dir.is_dir() and any(
        path.suffix == ".py" and path.name != "__init__.py"
        for path in revisions_dir.iterdir()
    ):
        _run_project_command(
            [sys.executable, "-m", "flask", "--app", "app:create_app", "db", "upgrade"],
            root,
            environment,
        )
    _run_project_command(
        [sys.executable, "-m", "app.cli", "init-db"],
        root,
        environment,
    )

    command = [
        sys.executable,
        "-m",
        "gunicorn",
        "--workers",
        str(workers),
        "--threads",
        str(threads),
        "--timeout",
        str(timeout),
        "--bind",
        f"{host}:{port}",
        "app:create_app()",
    ]
    try:
        os.execvpe(sys.executable, command, environment)
    except OSError as error:
        raise click.ClickException(f"Could not start Gunicorn: {error}") from error


def _next_available_port(host: str, port: int) -> int:
    for candidate in range(port, 65536):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            try:
                probe.bind((host, candidate))
            except OSError:
                continue
            return candidate
    raise click.ClickException(f"No available port found at or above {port}")


def _print_startup_banner() -> None:
    click.echo(Figlet(font="big").renderText("VFLASK").rstrip())
    credit = "by Kigongo Vincent"
    border = "+" + "-" * (len(credit) + 2) + "+"
    click.echo("\n".join((
        border,
        f"| {credit} |",
        border,
    )))


def _project_environment(root: Path) -> dict[str, str]:
    if not (root / "app" / "__init__.py").is_file():
        raise click.ClickException(f"No generated Flask app found under {root}")
    env_file = root / ".env"
    env_example = root / ".env.example"
    if not env_file.exists() and env_example.is_file():
        shutil.copyfile(env_example, env_file)
    environment = os.environ.copy()
    environment["APP_ENV"] = "development"
    environment["PYTHONPATH"] = str(root)
    return environment


def _run_flask_db_command(project_root: str, arguments: list[str]) -> None:
    root = Path(project_root).expanduser().resolve()
    environment = _project_environment(root)
    _run_project_command(
        [sys.executable, "-m", "flask", "--app", "app:create_app", "db", *arguments],
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
