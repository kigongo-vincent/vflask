from pathlib import Path

from vflask.core.scaffolder import ModuleScaffolder, ProjectScaffolder


def test_project_scaffolder_creates_expected_files(tmp_path: Path) -> None:
    project_dir = tmp_path / "demo_app"
    ProjectScaffolder.render_project("demo_app", project_dir)

    assert (project_dir / "requirements.txt").exists()
    assert (project_dir / "docker-compose.yml").exists()
    assert (project_dir / "app" / "__init__.py").exists()
    assert (project_dir / "app" / "config.py").exists()
    assert (project_dir / "app" / "base.py").exists()


def test_module_scaffolder_creates_model_and_routes(tmp_path: Path) -> None:
    project_dir = tmp_path / "demo_app"
    ProjectScaffolder.render_project("demo_app", project_dir)
    ModuleScaffolder.create_module(
        project_dir,
        "sales",
        [
            {"name": "customer_name", "type": "string", "nullable": False, "unique": False, "index": True},
            {"name": "amount", "type": "float", "nullable": False, "unique": False, "index": False},
        ],
        roles=["admin", "editor"],
    )

    module_dir = project_dir / "app" / "modules" / "sales"
    assert (module_dir / "models.py").exists()
    assert (module_dir / "routes.py").exists()
    assert "role_required" in (module_dir / "routes.py").read_text()
    assert "customer_name" in (module_dir / "models.py").read_text()
