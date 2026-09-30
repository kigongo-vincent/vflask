"""Command line interface for vflask."""

from __future__ import annotations

from pathlib import Path

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


if __name__ == "__main__":
    cli()
