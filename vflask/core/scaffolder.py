"""Scaffolding logic for creating typed Flask projects and modules."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "templates"


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


def parse_field_spec(spec: str) -> dict[str, Any]:
    if not spec or ":" not in spec:
        raise ValueError(f"Invalid field definition: {spec!r}. Use name:type[:flag]")

    name, type_name, *flags = spec.split(":")
    name = name.strip()
    type_name = (type_name or "string").strip().lower()
    field = {
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
            "project/app/watcher.py.j2": project_dir / "app" / "watcher.py",
            "project/scripts/start.sh.j2": project_dir / "scripts" / "start.sh",
            "project/scripts/push.sh.j2": project_dir / "scripts" / "push.sh",
            "project/scripts/help.sh.j2": project_dir / "scripts" / "help.sh",
            "project/tests/conftest.py.j2": project_dir / "tests" / "conftest.py",
            "project/tests/helpers.py.j2": project_dir / "tests" / "helpers.py",
            "project/migrations/env.py.j2": project_dir / "migrations" / "env.py",
        }

        for template_name, output_path in files_to_render.items():
            output_path.parent.mkdir(parents=True, exist_ok=True)
            content = env.get_template(template_name).render(project_name=name)
            output_path.write_text(content, encoding="utf-8")
            if template_name.endswith(".sh.j2"):
                os.chmod(output_path, 0o755)

        generated_files = {
            "requirements.txt": "click==8.1.7\nFlask==3.1.0\nFlask-SQLAlchemy==3.1.1\nFlask-Migrate==4.0.7\nFlask-JWT-Extended==4.7.1\nFlask-Cors==5.0.0\npsycopg[binary]==3.3.6\npython-dotenv==1.0.1\nwatchdog==4.0.1\nrich==13.0.0\ngunicorn==23.0.0\npytest==8.3.1\n",
            ".env.example": "FLASK_APP=app:create_app\nFLASK_DEBUG=1\nSECRET_KEY=changeme\nDATABASE_URL=postgresql+psycopg://app:app@localhost:5432/app\nJWT_SECRET_KEY=super-secret\nREDIS_URL=redis://localhost:6379/0\nPORT=5000\n",
            "docker-compose.yml": """services:\n  db:\n    image: postgres:16\n    environment:\n      POSTGRES_DB: app\n      POSTGRES_USER: app\n      POSTGRES_PASSWORD: app\n    ports:\n      - "5432:5432"\n    volumes:\n      - postgres_data:/var/lib/postgresql/data\n\n  redis:\n    image: redis:7-alpine\n    ports:\n      - "6379:6379"\n\nvolumes:\n  postgres_data:\n""",
            "app/__init__.py": """from __future__ import annotations\n\nfrom flask import Flask\n\nfrom app.config import AppConfig\nfrom app.extensions import db, jwt, migrate\n\n\ndef create_app(config_object: type | None = None) -> Flask:\n    app = Flask(__name__)\n    app.config.from_object(config_object or AppConfig)\n\n    db.init_app(app)\n    jwt.init_app(app)\n    migrate.init_app(app, db)\n\n    from app.modules import register_modules\n\n    register_modules(app)\n\n    @app.get("/api/v1/health")\n    def healthcheck() -> tuple[dict, int]:\n        return {\"status\": \"ok\"}, 200\n\n    return app\n""",
            "app/config.py": """from __future__ import annotations\n\nimport os\n\n\nclass AppConfig:\n    SECRET_KEY = os.getenv("SECRET_KEY", "development-secret")\n    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql+psycopg://app:app@localhost:5432/app")\n    SQLALCHEMY_TRACK_MODIFICATIONS = False\n    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")\n    JSON_SORT_KEYS = False\n\n\nclass TestingConfig(AppConfig):\n    TESTING = True\n    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"\n""",
            "app/extensions.py": """from __future__ import annotations\n\nfrom flask_jwt_extended import JWTManager\nfrom flask_migrate import Migrate\nfrom flask_sqlalchemy import SQLAlchemy\n\ndb = SQLAlchemy()\nmigrate = Migrate()\njwt = JWTManager()\n""",
            "app/base/__init__.py": """from __future__ import annotations\n\nfrom functools import wraps\nfrom typing import Any\n\nfrom flask import jsonify\nfrom flask_jwt_extended import get_jwt_identity, jwt_required\n\nfrom app.base.query import apply_filters\n\n\ndef api_ok(data: Any | None = None, msg: str = "success", status: int = 200):\n    return jsonify({\"status\": status, \"msg\": msg, \"data\": data}), status\n\n\ndef api_error(msg: str, status: int = 400):\n    return jsonify({\"status\": status, \"msg\": msg, \"data\": None}), status\n\n\ndef paginated_response(data: list[Any], total: int, page: int, limit: int):\n    return api_ok({\"items\": data, \"total\": total, \"page\": page, \"limit\": limit})\n\n\ndef auth_required(view):\n    @wraps(view)\n    @jwt_required()\n    def wrapper(*args, **kwargs):\n        return view(*args, **kwargs)\n\n    return wrapper\n\n\ndef role_required(*roles: str):\n    def decorator(view):\n        @wraps(view)\n        @jwt_required()\n        def wrapper(*args, **kwargs):\n            identity = get_jwt_identity()\n            if not identity:\n                return api_error("Authentication required", 401)\n            if roles and identity not in roles:\n                return api_error("Forbidden", 403)\n            return view(*args, **kwargs)\n\n        return wrapper\n\n    return decorator\n\n\ndef get_user_id() -> int:\n    return int(get_jwt_identity())\n\n\n__all__ = ["api_ok", "api_error", "paginated_response", "auth_required", "role_required", "get_user_id", "apply_filters"]\n""",
            "app/base/query.py": """from __future__ import annotations\n\nfrom typing import Any\n\n\ndef apply_filters(query: Any, model: Any, columns: list[dict[str, Any]] | None, filterable: set[str] | None = None) -> Any:\n    \"\"\"Apply simple query filters for list endpoints.\"\"\"\n    for column in columns or []:\n        field_name = str(column.get("column") or column.get("name") or "").strip()\n        if not field_name or (filterable is not None and field_name not in filterable):\n            continue\n\n        operator = str(column.get("operator") or "eq").lower()\n        value = column.get("value")\n        if value is None:\n            continue\n\n        attr = getattr(model, field_name, None)\n        if attr is None:\n            continue\n\n        if operator in {\"eq\", \"equals\", \"is\"}:\n            query = query.filter(attr == value)\n        elif operator in {\"ne\", \"noteq\", \"not\"}:\n            query = query.filter(attr != value)\n        elif operator in {\"gt\", \"greaterthan\"}:\n            query = query.filter(attr > value)\n        elif operator in {\"lt\", \"lessthan\"}:\n            query = query.filter(attr < value)\n        elif operator in {\"like\", \"contains\", \"icontains\"}:\n            query = query.filter(attr.like(f"%{value}%"))\n        elif operator in {\"in\", \"contains_any\"}:\n            query = query.filter(attr.in_(value if isinstance(value, (list, tuple, set)) else [value]))\n\n    return query\n""",
            "app/shared/__init__.py": """from app.shared.models import Role, User\n""",
            "app/shared/mixins.py": """from __future__ import annotations\n\nfrom datetime import datetime\n\nfrom app.extensions import db\n\n\nclass TimestampMixin:\n    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)\n    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)\n\n\nclass SoftDeleteMixin:\n    deleted_at = db.Column(db.DateTime, nullable=True, default=None)\n\n    def soft_delete(self) -> None:\n        self.deleted_at = datetime.utcnow()\n\n    def restore(self) -> None:\n        self.deleted_at = None\n""",
            "app/shared/models.py": """from __future__ import annotations\n\nfrom datetime import datetime\n\nfrom werkzeug.security import check_password_hash, generate_password_hash\n\nfrom app.extensions import db\nfrom app.shared.mixins import SoftDeleteMixin, TimestampMixin\n\n\nclass Role(db.Model):\n    __tablename__ = "roles"\n\n    id = db.Column(db.Integer, primary_key=True)\n    name = db.Column(db.String(80), unique=True, nullable=False, index=True)\n    description = db.Column(db.String(255), nullable=True)\n\n\nuser_roles = db.Table(\n    "user_roles",\n    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),\n    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),\n)\n\n\nclass User(SoftDeleteMixin, TimestampMixin, db.Model):\n    __tablename__ = "users"\n\n    id = db.Column(db.Integer, primary_key=True)\n    email = db.Column(db.String(255), unique=True, nullable=False, index=True)\n    password_hash = db.Column(db.String(255), nullable=False)\n    name = db.Column(db.String(120), nullable=False)\n    is_active = db.Column(db.Boolean, default=True, nullable=False)\n    roles = db.relationship("Role", secondary=user_roles, backref=db.backref("users", lazy="dynamic"))\n\n    def set_password(self, password: str) -> None:\n        self.password_hash = generate_password_hash(password)\n\n    def check_password(self, password: str) -> bool:\n        return check_password_hash(self.password_hash, password)\n\n    def to_dict(self) -> dict:\n        return {\n            "id": self.id,\n            "email": self.email,\n            "name": self.name,\n            "isActive": self.is_active,\n            "roles": [role.name for role in self.roles],\n        }\n""",
            "app/shared/rbac.py": """from __future__ import annotations\n\nfrom app.extensions import db\nfrom app.shared.models import Role, User\n\n\nclass RBACService:\n    @staticmethod\n    def seed_roles() -> None:\n        defaults = [\n            ("admin", "Full access"),\n            ("editor", "Can edit records"),\n            ("viewer", "Read-only access"),\n        ]\n        for name, description in defaults:\n            if not db.session.query(Role).filter_by(name=name).first():\n                db.session.add(Role(name=name, description=description))\n        db.session.commit()\n\n    @staticmethod\n    def assign_role(user: User, role_name: str) -> None:\n        role = db.session.query(Role).filter_by(name=role_name).first()\n        if role and role not in user.roles:\n            user.roles.append(role)\n            db.session.commit()\n\n    @staticmethod\n    def user_has_role(user: User, *required_roles: str) -> bool:\n        if not required_roles:\n            return True\n        if not user:\n            return False\n        names = {role.name for role in user.roles}\n        return bool(set(required_roles) & names)\n""",
            "app/modules/__init__.py": """from __future__ import annotations\n\nfrom importlib import import_module\nfrom pathlib import Path\n\nfrom flask import Flask\n\n\ndef register_modules(app: Flask) -> None:\n    modules_dir = Path(__file__).resolve().parent\n    for child in sorted(modules_dir.iterdir()):\n        if child.is_dir() and (child / "routes.py").exists():\n            module = import_module(f"app.modules.{child.name}.routes")\n            if hasattr(module, "register_routes"):\n                module.register_routes(app)\n""",
            "app/modules/.gitkeep": "",
        }
        for relative_path, content in generated_files.items():
            file_path = project_dir / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if relative_path.endswith(".gitkeep"):
                file_path.touch(exist_ok=True)
                continue
            file_path.write_text(content, encoding="utf-8")

        return project_dir



class ModuleScaffolder:
    """Create a module inside a generated Flask project."""

    @staticmethod
    def create_module(project_root: str | Path, module_name: str, fields: list[dict[str, Any]] | None = None, roles: list[str] | None = None, crud_mode: str = "crud") -> Path:
        root = Path(project_root).expanduser().resolve()
        module_key = re.sub(r"[^a-zA-Z0-9_]+", "_", module_name).strip("_").lower() or "module"
        class_name = "".join(part.capitalize() for part in module_key.split("_"))
        plural_name = module_key if module_key.endswith("s") else f"{module_key}s"
        singular_name = module_key
        normalized_mode = (crud_mode or "crud").lower().strip()
        if normalized_mode not in {"c", "cr", "crd", "crud"}:
            raise ValueError(f"Unsupported CRUD mode: {crud_mode!r}. Use c, cr, crd, or crud.")

        module_dir = root / "app" / "modules" / plural_name
        module_dir.mkdir(parents=True, exist_ok=True)

        env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_ROOT)),
            autoescape=select_autoescape(["html", "xml", "md"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        context = {
            "module": {
                "name": module_key,
                "plural_class": class_name if class_name.endswith("s") else class_name,
                "class_name": class_name,
                "table_name": plural_name,
                "singular": singular_name,
                "url_prefix": f"/api/v1/{plural_name}",
            },
            "fields": [
                {
                    **field,
                    "sqlalchemy_type": FieldSpec(**field).sqlalchemy_type,
                }
                for field in (fields or [])
            ],
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

        return module_dir


__all__ = ["FieldSpec", "ProjectScaffolder", "ModuleScaffolder", "parse_field_spec"]
