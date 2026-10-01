"""Scaffolding logic for creating typed Flask projects and modules."""

from __future__ import annotations

import ast
import os
import re
import venv
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict
from uuid import uuid4

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "templates"


class FieldData(TypedDict):
    name: str
    type: str
    nullable: bool
    unique: bool
    index: bool
    default: str | None


class MigrationFieldData(TypedDict):
    name: str
    alembic_type: str
    nullable: bool
    unique: bool
    index: bool


class ModuleTemplateField(FieldData):
    sqlalchemy_type: str
    python_type: str
    alembic_type: str
    test_value: str


@dataclass(slots=True)
class FieldSpec:
    name: str
    type: str
    nullable: bool = False
    unique: bool = False
    index: bool = False
    default: str | None = None

    @property
    def sqlalchemy_type(self) -> str:
        mapping = {
            "string": "db.String(255)",
            "text": "db.Text",
            "integer": "db.Integer",
            "int": "db.Integer",
            "float": "db.Float",
            "decimal": "db.Numeric(10, 2)",
            "boolean": "db.Boolean",
            "bool": "db.Boolean",
            "date": "db.Date",
            "datetime": "db.DateTime",
            "json": "db.JSON",
            "uuid": "db.String(36)",
        }
        return mapping.get(self.type.lower(), "db.String(255)")

    @property
    def python_type(self) -> str:
        mapping = {
            "string": "str",
            "text": "str",
            "integer": "int",
            "int": "int",
            "float": "float",
            "decimal": "Decimal",
            "boolean": "bool",
            "bool": "bool",
            "date": "date",
            "datetime": "datetime",
            "json": "JSONObject",
            "uuid": "str",
        }
        return mapping.get(self.type.lower(), "str")


def parse_field_spec(spec: str) -> FieldData:
    if not spec or ":" not in spec:
        raise ValueError(f"Invalid field definition: {spec!r}. Use name:type[:flag]")

    name, type_name, *flags = spec.split(":")
    name = name.strip()
    type_name = (type_name or "string").strip().lower()
    field: FieldData = {
        "name": name,
        "type": type_name,
        "nullable": True,
        "unique": False,
        "index": False,
        "default": None,
    }

    for flag in flags:
        cleaned = flag.strip().lower()
        if not cleaned:
            continue
        if cleaned in {"required", "notnull", "nonnullable"}:
            field["nullable"] = False
        elif cleaned in {"unique"}:
            field["unique"] = True
        elif cleaned in {"index"}:
            field["index"] = True
        elif cleaned.startswith("default="):
            field["default"] = cleaned.split("=", 1)[1]
        elif cleaned in {"nullable"}:
            field["nullable"] = True

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        raise ValueError(f"Invalid field name: {name!r}")

    return field


def _latest_migration_revision(versions_dir: Path) -> str | None:
    revisions: dict[str, str | tuple[str, ...] | None] = {}
    for migration_path in sorted(versions_dir.glob("*.py")):
        if migration_path.name == "__init__.py":
            continue
        tree = ast.parse(migration_path.read_text(encoding="utf-8"))
        values: dict[str, object] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in {"revision", "down_revision"}:
                        values[target.id] = ast.literal_eval(node.value)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if node.target.id in {"revision", "down_revision"} and node.value is not None:
                    values[node.target.id] = ast.literal_eval(node.value)
        revision = values.get("revision")
        if isinstance(revision, str):
            down_revision = values.get("down_revision")
            if down_revision is not None and not isinstance(down_revision, (str, tuple)):
                raise ValueError(f"Unsupported down_revision in {migration_path}")
            revisions[revision] = down_revision

    referenced = {
        parent
        for down_revision in revisions.values()
        for parent in ((down_revision,) if isinstance(down_revision, str) else down_revision or ())
    }
    heads = set(revisions) - referenced
    if len(heads) > 1:
        raise ValueError("Multiple Alembic heads found; merge migration branches before creating a module")
    return next(iter(heads), None)


class ProjectScaffolder:
    """Scaffold a generated Flask project from Jinja2 templates."""

    @staticmethod
    def render_project(project_name: str, destination: str | Path = ".") -> Path:
        root = Path(destination).expanduser().resolve()
        name = project_name.strip()
        if not name:
            raise ValueError("Project name cannot be empty.")

        project_dir = root if root.name == name else root / name
        project_dir.mkdir(parents=True, exist_ok=True)

        env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_ROOT)),
            autoescape=select_autoescape(["html", "xml", "md"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        files_to_render = {
            "project/README.md.j2": project_dir / "README.md",
            "project/app/cli.py.j2": project_dir / "app" / "cli.py",
            "project/app/base/openapi.py.j2": project_dir / "app" / "base" / "openapi.py",
            "project/app/base/types.py.j2": project_dir / "app" / "base" / "types.py",
            "project/app/integrations/__init__.py.j2": project_dir / "app" / "integrations" / "__init__.py",
            "project/app/integrations/payment.py.j2": project_dir / "app" / "integrations" / "payment.py",
            "project/app/integrations/storage.py.j2": project_dir / "app" / "integrations" / "storage.py",
            "project/app/integrations/mailer.py.j2": project_dir / "app" / "integrations" / "mailer.py",
            "project/app/integrations/google_oauth.py.j2": project_dir / "app" / "integrations" / "google_oauth.py",
            "project/Dockerfile.j2": project_dir / "Dockerfile",
            "project/dockerignore.j2": project_dir / ".dockerignore",
            "project/scripts/entrypoint.sh.j2": project_dir / "scripts" / "entrypoint.sh",
            "project/workflows/ci.yml.j2": project_dir / ".github" / "workflows" / "ci.yml",
            "project/workflows/deploy.yml.j2": project_dir / ".github" / "workflows" / "deploy.yml",
            "project/scripts/start.sh.j2": project_dir / "scripts" / "start.sh",
            "project/scripts/push.sh.j2": project_dir / "scripts" / "push.sh",
            "project/scripts/help.sh.j2": project_dir / "scripts" / "help.sh",
            "project/tests/conftest.py.j2": project_dir / "tests" / "conftest.py",
            "project/tests/helpers.py.j2": project_dir / "tests" / "helpers.py",
            "project/migrations/env.py.j2": project_dir / "migrations" / "env.py",
            "project/migrations/script.py.mako.j2": project_dir / "migrations" / "script.py.mako",
        }

        for template_name, output_path in files_to_render.items():
            output_path.parent.mkdir(parents=True, exist_ok=True)
            content = env.get_template(template_name).render(project_name=name)
            output_path.write_text(content, encoding="utf-8")
            if template_name.endswith(".sh.j2"):
                os.chmod(output_path, 0o755)

        generated_files = {
            ".gitignore": ".env\n.venv/\nvenv/\n__pycache__/\n*.py[cod]\n.pytest_cache/\n.mypy_cache/\n.pyright/\n.coverage\nhtmlcov/\n.DS_Store\n",
            "requirements.txt": "vflask>=1.1.0,<2\nclick==8.1.7\nFlask==3.1.0\nFlask-SQLAlchemy==3.1.1\nFlask-Migrate==4.0.7\nFlask-JWT-Extended==4.7.1\nFlask-Cors==5.0.0\npsycopg[binary]==3.3.6\npython-dotenv==1.0.1\nwatchdog==4.0.1\nrich==13.0.0\npyfiglet>=1.0.2,<2\ngunicorn==23.0.0\nrequests>=2.32,<3\nboto3>=1.35,<2\ncloudinary>=1.41,<2\npytest==8.3.1\n",
            "requirements-dev.txt": "-r requirements.txt\npyright>=1.1.400,<2\n",
            "migrations/alembic.ini": """[alembic]
script_location = .
prepend_sys_path = .
sqlalchemy.url = driver://user:pass@localhost/dbname

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers = console
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
""",
            "migrations/versions/.gitkeep": "",
            "pyrightconfig.json": '{\n  "include": ["app", "tests", "migrations"],\n  "pythonVersion": "3.11",\n  "stubPath": "typings",\n  "typeCheckingMode": "standard",\n  "reportExplicitAny": "error",\n  "strict": ["app/base/types.py", "app/modules"],\n  "executionEnvironments": [\n    {\n      "root": ".",\n      "extraPaths": ["."]\n    }\n  ]\n}\n',
            ".env.example": "FLASK_APP=app:create_app\nFLASK_DEBUG=0\nSECRET_KEY=replace-with-a-random-secret\nDATABASE_URL=postgresql+psycopg://app:app@localhost:5432/app\nJWT_SECRET_KEY=replace-with-a-separate-random-secret\nREDIS_URL=redis://localhost:6379/0\nPORT=5000\nWEB_CONCURRENCY=3\nGUNICORN_THREADS=2\nPAYMENT_PROVIDER=flutterwave\nFLW_SECRET_KEY=\nSTORAGE_PROVIDER=s3\nS3_BUCKET=\nAWS_REGION=us-east-1\nCLOUDINARY_CLOUD_NAME=\nCLOUDINARY_API_KEY=\nCLOUDINARY_API_SECRET=\nMAIL_PROVIDER=smtp\nMAIL_FROM_ADDRESS=\nSMTP_HOST=\nSMTP_PORT=587\nSMTP_USERNAME=\nSMTP_PASSWORD=\nGOOGLE_CLIENT_ID=\nGOOGLE_CLIENT_SECRET=\nGOOGLE_REDIRECT_URI=\n",
            "docker-compose.yml": """services:\n  db:\n    image: postgres:16\n    environment:\n      POSTGRES_DB: app\n      POSTGRES_USER: app\n      POSTGRES_PASSWORD: app\n    ports:\n      - "5432:5432"\n    volumes:\n      - postgres_data:/var/lib/postgresql/data\n\n  redis:\n    image: redis:7-alpine\n    ports:\n      - "6379:6379"\n\nvolumes:\n  postgres_data:\n""",
            "app/__init__.py": """from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, Response, jsonify

from app.base.openapi import build_openapi_spec
from app.base.types import JSONObject, json_object
from app.auth.routes import register_auth_routes
from app.config import AppConfig
from app.extensions import db, jwt, migrate

API_PREFIX = "/api/v1"
HEALTH_ROUTE = "/api/v1/health"
OPENAPI_ROUTE = "/api/v1/openapi.json"
DOCS_ROUTE = "/api/v1/docs"
MODULES_ROUTE = "/api/v1/docs/modules.json"


def create_app(config_object: type | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object or AppConfig)

    if not app.testing and os.getenv("APP_ENV", "production").lower() != "development":
        for key in ("SECRET_KEY", "JWT_SECRET_KEY"):
            secret = os.getenv(key, "")
            if len(secret) < 32 or secret in {"development-secret", "jwt-secret", "replace-with-a-random-secret", "replace-with-a-separate-random-secret"}:
                raise RuntimeError(f"Set a unique production {key} with at least 32 characters")
        database_url = os.getenv("DATABASE_URL", "")
        if "@localhost" in database_url or "@127.0.0.1" in database_url:
            raise RuntimeError("Set DATABASE_URL to a reachable production database")

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from app.modules import register_modules

    register_modules(app)
    register_auth_routes(app)

    @app.get(HEALTH_ROUTE)
    def healthcheck() -> tuple[JSONObject, int]:
        return {"status": "ok"}, 200

    @app.get(OPENAPI_ROUTE)
    def openapi_document() -> tuple[JSONObject, int]:
        return build_openapi_spec(app), 200

    @app.get(DOCS_ROUTE)
    def api_docs() -> Response:
        return Response(f"<!doctype html><html><head><title>API documentation</title><link rel='stylesheet' href='https://unpkg.com/swagger-ui-dist@5/swagger-ui.css'></head><body><div id='swagger-ui'></div><script src='https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js'></script><script>SwaggerUIBundle({{url:'{API_PREFIX}/openapi.json',dom_id:'#swagger-ui'}});</script></body></html>", mimetype="text/html")

    @app.get(MODULES_ROUTE)
    def module_docs_index() -> tuple[JSONObject, int]:
        modules_dir = Path(__file__).resolve().parent / "modules"
        entries: list[JSONObject] = []
        docs_by_module: dict[str, str] = {}

        for module_dir in sorted(modules_dir.iterdir(), key=lambda item: item.name):
            if not module_dir.is_dir():
                continue
            docs_path = module_dir / "docs.md"
            if not docs_path.exists():
                continue
            module_name = module_dir.name
            docs_by_module[module_name] = docs_path.read_text(encoding="utf-8")
            entries.append(
                json_object({
                    "name": module_name,
                    "path": f"{API_PREFIX}/{module_name}",
                    "docs": f"{API_PREFIX}/docs/{module_name}",
                    "available": True,
                })
            )

        return json_object({
            "title": "API Documentation",
            "base_url": API_PREFIX,
            "modules": entries,
            "docs": docs_by_module,
        }), 200

    @app.get("/api/v1/docs/<module_name>")
    def module_docs(module_name: str) -> tuple[Response, int] | tuple[dict[str, str], int]:
        docs_path = Path(__file__).resolve().parent / "modules" / module_name / "docs.md"
        if not docs_path.is_file():
            return jsonify({"error": "Module documentation not found"}), 404
        return Response(docs_path.read_text(encoding="utf-8"), mimetype="text/markdown"), 200

    return app
""",
            "app/config.py": """from __future__ import annotations\n\nimport os\n\n\nclass AppConfig:\n    SECRET_KEY = os.getenv("SECRET_KEY", "development-secret")\n    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql+psycopg://app:app@localhost:5432/app")\n    SQLALCHEMY_TRACK_MODIFICATIONS = False\n    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}\n    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")\n    JSON_SORT_KEYS = False\n    MAX_CONTENT_LENGTH = 16 * 1024 * 1024\n    SESSION_COOKIE_HTTPONLY = True\n    SESSION_COOKIE_SAMESITE = "Lax"\n    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "true").lower() == "true"\n\n\nclass TestingConfig(AppConfig):\n    TESTING = True\n    SESSION_COOKIE_SECURE = False\n    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"\n""",
            "app/extensions.py": """from __future__ import annotations\n\nfrom flask_jwt_extended import JWTManager\nfrom flask_migrate import Migrate\nfrom flask_sqlalchemy import SQLAlchemy\n\ndb = SQLAlchemy()\nmigrate = Migrate()\njwt = JWTManager()\n""",
            "app/base/__init__.py": """from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, cast

from flask import Response, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.base.query import apply_filters
from app.base.types import JSONObject, JSONValue

P = ParamSpec("P")


def api_ok(data: JSONValue | None = None, msg: str = "success", status: int = 200) -> tuple[Response, int]:
    return jsonify({\"status\": status, \"msg\": msg, \"data\": data}), status


def api_error(msg: str, status: int = 400) -> tuple[Response, int]:
    return jsonify({\"status\": status, \"msg\": msg, \"data\": None}), status


def paginated_response(data: list[JSONObject], total: int, page: int, limit: int) -> tuple[Response, int]:
    return api_ok({\"items\": data, \"total\": total, \"page\": page, \"limit\": limit})


def auth_required(view: Callable[P, tuple[Response, int]]) -> Callable[P, tuple[Response, int]]:
    @wraps(view)
    @jwt_required()
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> tuple[Response, int]:
        return view(*args, **kwargs)

    return cast(Callable[P, tuple[Response, int]], wrapper)


def role_required(*roles: str) -> Callable[
    [Callable[P, tuple[Response, int]]], Callable[P, tuple[Response, int]]
]:
    def decorator(view: Callable[P, tuple[Response, int]]) -> Callable[P, tuple[Response, int]]:
        @wraps(view)
        @jwt_required()
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> tuple[Response, int]:
            identity = get_jwt_identity()
            if not identity:
                return api_error("Authentication required", 401)
            if roles and identity not in roles:
                return api_error("Forbidden", 403)
            return view(*args, **kwargs)

        return cast(Callable[P, tuple[Response, int]], wrapper)

    return decorator


def get_user_id() -> int:
    return int(get_jwt_identity())


__all__ = ["api_ok", "api_error", "paginated_response", "auth_required", "role_required", "get_user_id", "apply_filters"]
""",
            "app/base/query.py": """from __future__ import annotations\n\nfrom typing import Any\n\n\ndef apply_filters(query: Any, model: Any, columns: list[dict[str, Any]] | None, filterable: set[str] | None = None) -> Any:\n    \"\"\"Apply simple query filters for list endpoints.\"\"\"\n    for column in columns or []:\n        field_name = str(column.get("column") or column.get("name") or "").strip()\n        if not field_name or (filterable is not None and field_name not in filterable):\n            continue\n\n        operator = str(column.get("operator") or "eq").lower()\n        value = column.get("value")\n        if value is None:\n            continue\n\n        attr = getattr(model, field_name, None)\n        if attr is None:\n            continue\n\n        if operator in {\"eq\", \"equals\", \"is\"}:\n            query = query.filter(attr == value)\n        elif operator in {\"ne\", \"noteq\", \"not\"}:\n            query = query.filter(attr != value)\n        elif operator in {\"gt\", \"greaterthan\"}:\n            query = query.filter(attr > value)\n        elif operator in {\"lt\", \"lessthan\"}:\n            query = query.filter(attr < value)\n        elif operator in {\"like\", \"contains\", \"icontains\"}:\n            query = query.filter(attr.like(f"%{value}%"))\n        elif operator in {\"in\", \"contains_any\"}:\n            query = query.filter(attr.in_(value if isinstance(value, (list, tuple, set)) else [value]))\n\n    return query\n""",
            "app/auth/__init__.py": """from app.auth.routes import register_auth_routes

__all__ = ["register_auth_routes"]
""",
            "app/auth/routes.py": """from __future__ import annotations

import os
import random
import secrets

from flask import Blueprint, Flask, Response, current_app, request, url_for
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from itsdangerous import BadSignature, URLSafeTimedSerializer
from requests import RequestException

from app.base import api_error, api_ok
from app.base.types import JSONObject, json_object
from app.extensions import db
from app.integrations.google_oauth import GoogleOAuthClient
from app.shared.models import User

bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")
AUTH_LOGIN_URL = "/api/v1/auth/login"


def register_auth_routes(app: Flask) -> None:
    app.register_blueprint(bp)


def _google_state_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="google-oauth-state")


def _google_redirect_uri() -> str:
    return os.getenv("GOOGLE_REDIRECT_URI") or url_for("auth.google_oauth_callback", _external=True)


@bp.get("/google/authorization-url")
def google_authorization_url() -> tuple[Response, int]:
    try:
        client = GoogleOAuthClient.from_environment()
        state = _google_state_serializer().dumps({"nonce": secrets.token_urlsafe(32)})
        redirect_uri = _google_redirect_uri()
        return api_ok(
            {
                "authorization_url": client.authorization_url(redirect_uri=redirect_uri, state=state),
                "state": state,
                "redirect_uri": redirect_uri,
            }
        )
    except RuntimeError as error:
        return api_error(str(error), 503)


@bp.route("/google/callback", methods=["GET", "POST"])
def google_oauth_callback() -> tuple[Response, int]:
    payload = json_object(request.get_json(silent=True) or request.args.to_dict())
    code = str(payload.get("code", "")).strip()
    state = str(payload.get("state", "")).strip()
    if not code or not state:
        return api_error("code and state are required", 400)
    try:
        _google_state_serializer().loads(state, max_age=600)
    except BadSignature:
        return api_error("Invalid or expired OAuth state", 400)

    try:
        profile = GoogleOAuthClient.from_environment().process_callback(
            code=code,
            redirect_uri=_google_redirect_uri(),
        )
    except RuntimeError as error:
        return api_error(str(error), 503)
    except RequestException:
        return api_error("Google OAuth request failed", 502)

    email = str(profile.get("email", "")).strip().lower()
    if not email or profile.get("email_verified") is not True:
        return api_error("Google account must have a verified email address", 401)

    user = db.session.query(User).filter_by(email=email).first()
    if not user:
        user = User()
        user.email = email
        user.name = str(profile.get("name") or email)
        user.is_active = True
        user.set_password(secrets.token_urlsafe(32))
        db.session.add(user)
        db.session.commit()
    if not user.is_active:
        return api_error("User account is inactive", 403)

    return api_ok(
        {
            "token": create_access_token(identity=str(user.id)),
            "refresh_token": create_refresh_token(identity=str(user.id)),
            "user": _serialize_user(user),
        },
        msg="Google sign-in successful",
    )


def _serialize_user(user: User) -> JSONObject:
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "isActive": user.is_active,
        "roles": [role.name for role in user.roles],
    }


@bp.post("/signup")
def signup() -> tuple[Response, int]:
    payload = json_object(request.get_json(silent=True))
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", "")).strip()
    name = str(payload.get("name", "")).strip()

    if not email or not password or not name:
        return api_error("email, password, and name are required", 400)

    if db.session.query(User).filter_by(email=email).first():
        return api_error("User already exists", 409)

    user = User()
    user.email = email
    user.name = name
    user.is_active = True
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access = create_access_token(identity=str(user.id))
    refresh = create_refresh_token(identity=str(user.id))
    return api_ok(
        {"token": access, "refresh_token": refresh, "user": _serialize_user(user)},
        msg="signup successful",
        status=201,
    )


@bp.post("/login")
def login() -> tuple[Response, int]:
    payload = json_object(request.get_json(silent=True))
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", "")).strip()

    if not email or not password:
        return api_error("email and password are required", 400)

    user = db.session.query(User).filter_by(email=email).first()
    if not user or not user.check_password(password):
        return api_error("Invalid email or password", 401)

    access = create_access_token(identity=str(user.id))
    refresh = create_refresh_token(identity=str(user.id))
    return api_ok({"token": access, "refresh_token": refresh, "user": _serialize_user(user)})


@bp.get("/verify-token")
@jwt_required()
def verify_token() -> tuple[Response, int]:
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return api_error("Invalid token", 401)
    return api_ok({"valid": True, "user": _serialize_user(user)})


@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh_token() -> tuple[Response, int]:
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return api_error("User not found", 404)
    access = create_access_token(identity=str(user.id))
    refresh = create_refresh_token(identity=str(user.id))
    return api_ok({"token": access, "refresh_token": refresh, "user": _serialize_user(user)})


@bp.post("/request-otp")
def request_otp() -> tuple[Response, int]:
    payload = json_object(request.get_json(silent=True))
    email = str(payload.get("email", "")).strip().lower()
    if not email:
        return api_error("email is required", 400)

    user = db.session.query(User).filter_by(email=email).first()
    if not user:
        return api_error("User not found", 404)

    otp = str(random.randint(100000, 999999))
    return api_ok({"otp": otp, "message": "OTP generated for password reset"})


@bp.post("/forgot-password")
def forgot_password() -> tuple[Response, int]:
    payload = json_object(request.get_json(silent=True))
    email = str(payload.get("email", "")).strip().lower()
    if not email:
        return api_error("email is required", 400)

    user = db.session.query(User).filter_by(email=email).first()
    if not user:
        return api_error("User not found", 404)

    otp = str(random.randint(100000, 999999))
    return api_ok({"otp": otp, "message": "Password reset OTP sent"})


@bp.post("/reset-password")
def reset_password() -> tuple[Response, int]:
    payload = json_object(request.get_json(silent=True))
    email = str(payload.get("email", "")).strip().lower()
    otp = str(payload.get("otp", "")).strip()
    password = str(payload.get("password", "")).strip()

    if not email or not otp or not password:
        return api_error("email, otp, and password are required", 400)

    user = db.session.query(User).filter_by(email=email).first()
    if not user:
        return api_error("User not found", 404)

    if len(otp) != 6 or not otp.isdigit():
        return api_error("Invalid OTP", 400)

    user.set_password(password)
    db.session.commit()
    return api_ok({"message": "Password reset successful"})


@bp.get("/me")
@jwt_required()
def me() -> tuple[Response, int]:
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return api_error("User not found", 404)
    return api_ok({"user": _serialize_user(user)})


@bp.put("/profile")
@jwt_required()
def update_profile() -> tuple[Response, int]:
    payload = json_object(request.get_json(silent=True))
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return api_error("User not found", 404)

    if "name" in payload and str(payload.get("name", "")).strip():
        user.name = str(payload["name"]).strip()
    if "email" in payload and str(payload.get("email", "")).strip():
        user.email = str(payload["email"]).strip().lower()
    if "password" in payload and str(payload.get("password", "")).strip():
        user.set_password(str(payload["password"]).strip())

    db.session.commit()
    return api_ok({"user": _serialize_user(user)}, msg="profile updated")


@bp.post("/logout")
@jwt_required()
def logout() -> tuple[Response, int]:
    return api_ok({"message": "logged out"})
""",
            "app/shared/__init__.py": """from app.shared.models import Role, User

__all__ = ["Role", "User"]
""",
            "app/shared/mixins.py": """from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(db.DateTime, nullable=True, default=None)

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        self.deleted_at = None
""",
            "app/shared/models.py": """from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app.base.types import JSONObject, to_json_value
from app.extensions import db
from app.shared.mixins import SoftDeleteMixin, TimestampMixin


class Role(db.Model):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(80), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(db.String(255), nullable=True)
    users: Mapped[list["User"]] = relationship(secondary="user_roles", back_populates="roles")


user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
)


class User(SoftDeleteMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(db.String(255), nullable=False)
    name: Mapped[str] = mapped_column(db.String(120), nullable=False)
    is_active: Mapped[bool] = mapped_column(db.Boolean, default=True, nullable=False)
    roles: Mapped[list[Role]] = relationship(secondary=user_roles, back_populates="users")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> JSONObject:
        return {
            "id": to_json_value(self.id),
            "email": self.email,
            "name": self.name,
            "isActive": self.is_active,
            "roles": [role.name for role in self.roles],
        }
""",
            "app/shared/rbac.py": """from __future__ import annotations\n\nfrom app.extensions import db\nfrom app.shared.models import Role, User\n\n\nclass RBACService:\n    @staticmethod\n    def seed_roles() -> None:\n        defaults = [\n            ("admin", "Full access"),\n            ("editor", "Can edit records"),\n            ("viewer", "Read-only access"),\n        ]\n        for name, description in defaults:\n            if not db.session.query(Role).filter_by(name=name).first():\n                db.session.add(Role(name=name, description=description))\n        db.session.commit()\n\n    @staticmethod\n    def assign_role(user: User, role_name: str) -> None:\n        role = db.session.query(Role).filter_by(name=role_name).first()\n        if role and role not in user.roles:\n            user.roles.append(role)\n            db.session.commit()\n\n    @staticmethod\n    def user_has_role(user: User, *required_roles: str) -> bool:\n        if not required_roles:\n            return True\n        if not user:\n            return False\n        names = {role.name for role in user.roles}\n        return bool(set(required_roles) & names)\n""",
            "app/modules/__init__.py": """from __future__ import annotations\n\nfrom importlib import import_module\nfrom pathlib import Path\n\nfrom flask import Flask\n\n\ndef register_modules(app: Flask) -> None:\n    modules_dir = Path(__file__).resolve().parent\n    for child in sorted(modules_dir.iterdir()):\n        if child.is_dir() and (child / "routes.py").exists():\n            module = import_module(f"app.modules.{child.name}.routes")\n            if hasattr(module, "register_routes"):\n                module.register_routes(app)\n""",
            "app/modules/.gitkeep": "",
            "typings/pyfiglet/__init__.pyi": "class Figlet:\n    def __init__(self, font: str = ...) -> None: ...\n    def renderText(self, text: str) -> str: ...\n",
        }
        generated_files["docker-compose.yml"] = env.get_template("project/docker-compose.yml.j2").render()
        generated_files["app/base/query.py"] = env.get_template("project/app/base/query.py.j2").render()
        generated_files["app/shared/rbac.py"] = env.get_template("project/app/shared/rbac.py.j2").render()
        for relative_path, content in generated_files.items():
            file_path = project_dir / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if relative_path.endswith(".gitkeep"):
                file_path.touch(exist_ok=True)
                continue
            file_path.write_text(content, encoding="utf-8")

        venv_python = project_dir / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        if not venv_python.is_file():
            venv.create(project_dir / ".venv", with_pip=True)

        return project_dir



class ModuleScaffolder:
    """Create a module inside a generated Flask project."""

    @staticmethod
    def create_module(project_root: str | Path, module_name: str, fields: list[FieldData] | None = None, roles: list[str] | None = None, crud_mode: str = "crud") -> Path:
        root = Path(project_root).expanduser().resolve()
        module_key = re.sub(r"[^a-zA-Z0-9_]+", "_", module_name).strip("_").lower() or "module"
        class_name = "".join(part.capitalize() for part in module_key.split("_"))
        plural_name = module_key if module_key.endswith("s") else f"{module_key}s"
        singular_name = module_key
        normalized_mode = (crud_mode or "crud").lower().strip()
        if normalized_mode not in {"c", "cr", "crd", "crud"}:
            raise ValueError(f"Unsupported CRUD mode: {crud_mode!r}. Use c, cr, crd, or crud.")

        module_dir = root / "app" / "modules" / plural_name
        is_new_module = not (module_dir / "models.py").exists()
        module_dir.mkdir(parents=True, exist_ok=True)

        env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_ROOT)),
            autoescape=select_autoescape(["html", "xml", "md"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        test_values = {
            "string": '"example"',
            "text": '"example"',
            "integer": "1",
            "int": "1",
            "float": "1.5",
            "decimal": "1.5",
            "boolean": "True",
            "bool": "True",
            "date": "datetime.now(timezone.utc).date()",
            "datetime": "datetime.now(timezone.utc)",
            "json": '{"key": "value"}',
            "uuid": '"00000000-0000-0000-0000-000000000000"',
        }
        module_context = {
                "name": module_key,
                "plural_class": class_name if class_name.endswith("s") else class_name,
                "class_name": class_name,
                "table_name": plural_name,
                "singular": singular_name,
                "url_prefix": f"/api/v1/{plural_name}",
            }
        module_fields: list[ModuleTemplateField] = [
                {
                    **field,
                    "sqlalchemy_type": FieldSpec(**field).sqlalchemy_type,
                    "python_type": FieldSpec(**field).python_type,
                    "alembic_type": FieldSpec(**field).sqlalchemy_type.replace("db.", "sa."),
                    "test_value": test_values.get(field["type"].lower(), '"example"'),
                }
                for field in (fields or [])
            ]
        context: dict[str, object] = {
            "module": module_context,
            "fields": module_fields,
            "needs_date_import": any(field["type"].lower() in {"date", "datetime"} for field in (fields or [])),
            "needs_decimal_import": any(field["type"].lower() == "decimal" for field in (fields or [])),
            "roles": list(roles or ["admin"]),
            "crud_mode": normalized_mode,
        }

        for template_name, out_name in {
            "module/__init__.py.j2": "__init__.py",
            "module/models.py.j2": "models.py",
            "module/services.py.j2": "service.py",
            "module/handlers.py.j2": "handlers.py",
            "module/routes.py.j2": "routes.py",
            "module/docs.md.j2": "docs.md",
            "module/test_module.py.j2": "test_module.py",
        }.items():
            content = env.get_template(template_name).render(**context)
            (module_dir / out_name).write_text(content, encoding="utf-8")

        versions_dir = root / "migrations" / "versions"
        if is_new_module and versions_dir.is_dir():
            migration_fields: list[MigrationFieldData] = [
                {
                    "name": field["name"],
                    "alembic_type": field["alembic_type"],
                    "nullable": field["nullable"],
                    "unique": field["unique"],
                    "index": field["index"],
                }
                for field in module_fields
            ]
            if not migration_fields:
                migration_fields = [{
                    "name": "name",
                    "alembic_type": "sa.String(255)",
                    "nullable": False,
                    "unique": False,
                    "index": True,
                }]
            revision = uuid4().hex[:12]
            migration_content = env.get_template("module/migration.py.j2").render(
                module=module_context,
                fields=migration_fields,
                revision=revision,
                revision_literal=repr(revision),
                down_revision_literal=repr(_latest_migration_revision(versions_dir)),
            )
            (versions_dir / f"{revision}_create_{plural_name}.py").write_text(
                migration_content,
                encoding="utf-8",
            )

        return module_dir


__all__ = ["FieldSpec", "ProjectScaffolder", "ModuleScaffolder", "parse_field_spec"]
