import ast
from pathlib import Path

from vflask.core.scaffolder import ModuleScaffolder, ProjectScaffolder


def test_project_scaffolder_creates_expected_files(tmp_path: Path) -> None:
    project_dir = tmp_path / "demo_app"
    ProjectScaffolder.render_project("demo_app", project_dir)

    assert (project_dir / "requirements.txt").exists()
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
    assert (project_dir / "app" / "integrations" / "payment.py").exists()
    assert (project_dir / "app" / "integrations" / "storage.py").exists()
    assert (project_dir / "app" / "integrations" / "mailer.py").exists()
    assert (project_dir / "app" / "integrations" / "google_oauth.py").exists()
    assert (project_dir / "Dockerfile").exists()
    assert (project_dir / ".dockerignore").exists()
    assert (project_dir / ".github" / "workflows" / "ci.yml").exists()
    assert (project_dir / ".github" / "workflows" / "deploy.yml").exists()
    for generated_python in project_dir.rglob("*.py"):
        ast.parse(generated_python.read_text(), filename=str(generated_python))
    app_init = (project_dir / "app" / "__init__.py").read_text()
    assert '"/api/v1/openapi.json"' in app_init
    assert '"/api/v1/docs"' in app_init
    payment = (project_dir / "app" / "integrations" / "payment.py").read_text()
    storage = (project_dir / "app" / "integrations" / "storage.py").read_text()
    mailer = (project_dir / "app" / "integrations" / "mailer.py").read_text()
    oauth = (project_dir / "app" / "integrations" / "google_oauth.py").read_text()
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

    module_dir = project_dir / "app" / "modules" / "sales"
    handlers_text = (module_dir / "handlers.py").read_text()
    models_text = (module_dir / "models.py").read_text()
    openapi_text = (project_dir / "app" / "base" / "openapi.py").read_text()

    assert (module_dir / "models.py").exists()
    assert (module_dir / "routes.py").exists()
    assert (module_dir / "docs.md").exists()
    assert (module_dir / "test_module.py").exists()
    module_tests = (module_dir / "test_module.py").read_text()
    ast.parse(module_tests)
    assert "serialization_returns_declared_fields" in module_tests
    assert 'assert "createdAt" in data' in module_tests
    routes_text = (module_dir / "routes.py").read_text()
    assert "role_required" in routes_text
    assert "def register_routes(app: Flask) -> None:" in routes_text
    assert "customer_name" in models_text
    assert "def to_dict(self) -> dict[str, Any]:" in models_text
    assert "def list(self) -> tuple[Response, int]:" in handlers_text
    assert "pagination with page and limit required" in handlers_text
    assert "limit > 100" in handlers_text
    assert "db.Model.registry.mappers" in openapi_text
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
