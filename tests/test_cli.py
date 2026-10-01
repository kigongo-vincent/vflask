import ast
import tomllib
from types import SimpleNamespace
from pathlib import Path

from click.testing import CliRunner

import vflask
from vflask.cli.main import cli
from vflask.core.scaffolder import ModuleScaffolder, ProjectScaffolder


def test_package_version_matches_pyproject() -> None:
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text())

    assert vflask.__version__ == data["project"]["version"]


def test_generated_app_cli_uses_project_commands_instead_of_manual_scripts(tmp_path: Path) -> None:
    project_dir = tmp_path / "demo_app"
    ProjectScaffolder.render_project("demo_app", project_dir)

    cli_text = (project_dir / "app" / "cli.py").read_text()
    readme = (project_dir / "README.md").read_text()

    assert '@main.command("run")' in cli_text
    assert '@main.command("push")' in cli_text
    assert 'subprocess.run(["git", "push"]' in cli_text
    assert './scripts/push.sh' not in readme
    assert 'python -m app.cli push' in readme


def test_project_scaffolder_creates_expected_files(tmp_path: Path) -> None:
    project_dir = tmp_path / "demo_app"
    ProjectScaffolder.render_project("demo_app", project_dir)

    assert (project_dir / "requirements.txt").exists()
    assert (project_dir / "requirements-dev.txt").exists()
    assert (project_dir / "docker-compose.yml").exists()
    assert (project_dir / "migrations" / "alembic.ini").exists()
    assert (project_dir / "migrations" / "script.py.mako").exists()
    assert (project_dir / "migrations" / "versions" / ".gitkeep").exists()
    assert (project_dir / "pyrightconfig.json").exists()
    assert (project_dir / "app" / "__init__.py").exists()
    assert (project_dir / "app" / "config.py").exists()
    assert (project_dir / "app" / "base" / "__init__.py").exists()
    assert (project_dir / "app" / "base" / "query.py").exists()
    assert (project_dir / "app" / "base" / "openapi.py").exists()
    assert (project_dir / "app" / "base" / "types.py").exists()
    assert (project_dir / "app" / "integrations" / "payment.py").exists()
    assert (project_dir / "app" / "integrations" / "storage.py").exists()
    assert (project_dir / "app" / "integrations" / "mailer.py").exists()
    assert (project_dir / "app" / "integrations" / "google_oauth.py").exists()
    assert (project_dir / "Dockerfile").exists()
    assert (project_dir / "scripts" / "entrypoint.sh").exists()
    assert (project_dir / ".dockerignore").exists()
    assert (project_dir / ".github" / "workflows" / "ci.yml").exists()
    assert (project_dir / ".github" / "workflows" / "deploy.yml").exists()
    project_readme = (project_dir / "README.md").read_text()
    assert "/api/v1/openapi.json" in project_readme
    assert "GOOGLE_CLIENT_ID" in project_readme
    assert "EC2_SSH_KEY" in project_readme
    compose_text = (project_dir / "docker-compose.yml").read_text()
    assert all(f"  {service}:" in compose_text for service in ("app", "db", "redis"))
    assert "postgresql+psycopg://app:app@db:5432/app" in compose_text
    assert "redis://redis:6379/0" in compose_text
    assert "condition: service_healthy" in compose_text
    ci_workflow = (project_dir / ".github" / "workflows" / "ci.yml").read_text()
    assert "docker compose up --build --detach --wait app" in ci_workflow
    assert "/api/v1/health" in ci_workflow
    assert "pyright" in ci_workflow
    pyright_config = (project_dir / "pyrightconfig.json").read_text()
    assert '"reportExplicitAny": "error"' in pyright_config
    assert '"app/modules"' in pyright_config
    for generated_python in project_dir.rglob("*.py"):
        ast.parse(generated_python.read_text(), filename=str(generated_python))
    app_init = (project_dir / "app" / "__init__.py").read_text()
    assert '"/api/v1/openapi.json"' in app_init
    assert '"/api/v1/docs"' in app_init
    entrypoint = (project_dir / "scripts" / "entrypoint.sh").read_text()
    assert "db upgrade" in entrypoint
    assert "-m app.cli init-db" in entrypoint
    assert "entrypoint.sh" in (project_dir / "Dockerfile").read_text()
    start_script = (project_dir / "scripts" / "start.sh").read_text()
    assert "python -m app.cli run" in start_script
    init_command = (project_dir / "app" / "cli.py").read_text()
    assert "db.create_all()" in init_command
    assert "RBACService.seed_roles()" in init_command
    assert "Admin123!" not in init_command
    payment = (project_dir / "app" / "integrations" / "payment.py").read_text()
    storage = (project_dir / "app" / "integrations" / "storage.py").read_text()
    mailer = (project_dir / "app" / "integrations" / "mailer.py").read_text()
    oauth = (project_dir / "app" / "integrations" / "google_oauth.py").read_text()
    assert "Any" not in payment + storage + mailer + oauth
    assert 'os.getenv("PAYMENT_PROVIDER", "flutterwave")' in payment
    assert 'os.getenv("STORAGE_PROVIDER", "s3")' in storage
    assert "CloudinaryStorageProvider" in storage
    assert 'os.getenv("MAIL_PROVIDER", "smtp")' in mailer
    assert "AWSSESMailProvider" in mailer
    assert "token_endpoint" in oauth and "userinfo_endpoint" in oauth
    deploy_workflow = (project_dir / ".github" / "workflows" / "deploy.yml").read_text()
    for secret in ("DOCKER_PAT", "DOCKER_USERNAME", "EC2_HOST", "EC2_SSH_KEY", "EC2_USER", "ENV_FILE", "PROJECT_NAME"):
        assert secret in deploy_workflow
    assert "flask --app app:create_app db upgrade" in deploy_workflow
    env_example = (project_dir / ".env.example").read_text()
    assert "FLW_SECRET_KEY" in env_example
    assert "GOOGLE_CLIENT_SECRET" in env_example


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
        crud_mode="crud",
    )
    migration_files = list((project_dir / "migrations" / "versions").glob("*.py"))
    assert len(migration_files) == 1
    migration_text = migration_files[0].read_text()
    ast.parse(migration_text)
    assert 'op.create_table(' in migration_text
    assert 'sa.Column("customer_name", sa.String(255), nullable=False)' in migration_text
    assert "op.create_index(" in migration_text
    assert '"ix_sales_customer_name"' in migration_text

    ModuleScaffolder.create_module(
        project_dir,
        "sales",
        [
            {"name": "customer_name", "type": "string", "nullable": False, "unique": False, "index": True},
            {"name": "amount", "type": "float", "nullable": False, "unique": False, "index": False},
        ],
        roles=["admin", "editor"],
        crud_mode="crud",
    )
    assert len(list((project_dir / "migrations" / "versions").glob("*.py"))) == 1

    ModuleScaffolder.create_module(
        project_dir,
        "inventory",
        [{"name": "sku", "type": "string", "nullable": False, "unique": True, "index": False}],
    )
    chained_migrations = list((project_dir / "migrations" / "versions").glob("*.py"))
    assert len(chained_migrations) == 2
    first_revision = next(
        ast.literal_eval(node.value)
        for node in ast.parse(migration_text).body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "revision" for target in node.targets)
    )
    inventory_migration = next(path for path in chained_migrations if "inventory" in path.name)
    inventory_tree = ast.parse(inventory_migration.read_text())
    down_revision = next(
        ast.literal_eval(node.value)
        for node in inventory_tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "down_revision" for target in node.targets)
    )
    assert down_revision == first_revision

    module_dir = project_dir / "app" / "modules" / "sales"
    handlers_text = (module_dir / "handlers.py").read_text()
    models_text = (module_dir / "models.py").read_text()
    services_text = (module_dir / "service.py").read_text()
    openapi_text = (project_dir / "app" / "base" / "openapi.py").read_text()

    assert (module_dir / "models.py").exists()
    assert (module_dir / "routes.py").exists()
    assert (module_dir / "docs.md").exists()
    assert (module_dir / "test_module.py").exists()
    module_tests = (module_dir / "test_module.py").read_text()
    module_docs = (module_dir / "docs.md").read_text()
    ast.parse(module_tests)
    assert "serialization_returns_declared_fields" in module_tests
    assert 'assert "createdAt" in data' in module_tests
    assert "/api/v1/openapi.json" in module_docs
    assert "maximum limit is 100" in module_docs
    assert "test_module.py" in module_docs
    routes_text = (module_dir / "routes.py").read_text()
    assert "role_required" in routes_text
    assert "def register_routes(app: Flask) -> None:" in routes_text
    assert "customer_name" in models_text
    assert "def to_dict(self) -> JSONObject:" in models_text
    assert "Any" not in handlers_text + models_text + services_text
    assert "def list(self) -> tuple[Response, int]:" in handlers_text
    assert "pagination with page and limit required" in handlers_text
    assert "limit > 100" in handlers_text
    assert "import_module(f\"app.modules.{module_dir.name}.models\")" in openapi_text
    assert "inspect(model)" in openapi_text
    assert '"items": {"type": "array", "items": _reference(model_name)}' in openapi_text
    assert '"customer_name"' in models_text
    assert '"amount"' in models_text
    assert "datetime.now(timezone.utc)" in (project_dir / "app" / "shared" / "mixins.py").read_text()


def test_project_scaffolder_includes_auth_and_docs_routes(tmp_path: Path) -> None:
    project_dir = tmp_path / "demo_app"
    ProjectScaffolder.render_project("demo_app", project_dir)

    auth_routes = (project_dir / "app" / "auth" / "routes.py").read_text()
    app_init = (project_dir / "app" / "__init__.py").read_text()

    assert "/api/v1/auth/login" in auth_routes
    assert "signup" in auth_routes
    assert "verify_token" in auth_routes
    assert "refresh_token" in auth_routes
    assert "request_otp" in auth_routes
    assert "forgot_password" in auth_routes
    assert "reset_password" in auth_routes
    assert "update_profile" in auth_routes
    assert "google_authorization_url" in auth_routes
    assert "google_oauth_callback" in auth_routes
    assert "Invalid or expired OAuth state" in auth_routes
    assert '"/api/v1/docs"' in app_init
    openapi_text = (project_dir / "app" / "base" / "openapi.py").read_text()
    assert '"signup": ("email", "password", "name")' in openapi_text
    assert '"BearerAuth"' in openapi_text
    assert '"openapi": "3.0.3"' in openapi_text
    assert '"google_authorization_url"' in openapi_text
    assert '"google_oauth_callback"' in openapi_text


def test_vflask_run_starts_services_bootstraps_database_and_runs_app(tmp_path: Path, monkeypatch) -> None:
    project_dir = tmp_path / "demo_app"
    ProjectScaffolder.render_project("demo_app", project_dir)
    calls: list[list[str]] = []

    def fake_run(command: list[str], **kwargs) -> SimpleNamespace:
        calls.append(command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr("vflask.cli.main.subprocess.run", fake_run)
    result = CliRunner().invoke(cli, ["run", "--project-root", str(project_dir)])

    assert result.exit_code == 0, result.output
    assert calls[0][:5] == ["docker", "compose", "up", "-d", "--wait"]
    assert calls[1][0:3] == ["docker", "compose", "exec"]
    assert calls[2][1:4] == ["-m", "app.cli", "init-db"]
    assert calls[3][1:5] == ["-m", "flask", "--app", "app:create_app"]
