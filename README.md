# vflask

vflask is a typed Flask project scaffolder and module generator designed to feel like a lightweight Django-style workflow without requiring a full ORM abstraction layer or a rigid app structure. It creates runnable Flask applications with PostgreSQL defaults, Redis support, JWT auth, role-based access control, and generated module scaffolds for CRUD-style features.

This repository includes both:

- the reusable Python scaffolding library itself
- the CLI used to generate full starter projects and modules

The most important thing to understand is that vflask is not only a command-line generator. It is also a Python library with explicit scaffolding primitives you can call directly.

## 1. Installation

From a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

After installation, the CLI is available as:

```bash
vflask --help
```

## 2. CLI usage

### Create a project

```bash
vflask new myapp
```

Optional destination:

```bash
vflask new myapp --path /path/to/workspace
```

This creates a new project directory with a Flask app factory, config, extensions, base utilities, default RBAC models, Docker Compose setup, and scripts.

### Create a module inside an existing project

```bash
cd myapp
vflask module create sales \
  -f name:string:required \
  -f amount:float \
  -f status:string:index \
  -r admin \
  -r editor
```

The field format is:

```text
name:type[:flag]
```

Examples:

- `name:string`
- `amount:float`
- `status:string:index`
- `is_active:boolean:required`
- `email:string:unique`
- `created_at:datetime`

Flags supported by the field parser:

- `required` / `notnull` / `nonnullable`
- `unique`
- `index`
- `default=value`
- `nullable`

### Watch generated module files

```bash
vflask watch --project-root .
```

The watcher observes module changes and regenerates module docs automatically when a module's handlers change.

## 3. Python library usage

The library layer is the core of vflask. You can use it directly without invoking the terminal.

```python
from pathlib import Path

from vflask.core.scaffolder import (
    FieldSpec,
    ModuleScaffolder,
    ProjectScaffolder,
    parse_field_spec,
)

# Create a project programmatically
ProjectScaffolder.render_project("demoapp", Path("."))

# Parse a field definition
field = parse_field_spec("name:string:required")
print(field)
# {'name': 'name', 'type': 'string', 'nullable': False, 'unique': False, 'index': False, 'default': None}

# Create a module inside that project
ModuleScaffolder.create_module(
    "/path/to/demoapp",
    "sales",
    [
        parse_field_spec("name:string:required"),
        parse_field_spec("amount:float"),
        parse_field_spec("status:string:index"),
    ],
    ["admin", "editor"],
)
```

### FieldSpec and datatype mapping

The library includes a `FieldSpec` dataclass and SQLAlchemy type mapping. This is how generated models decide the underlying database column type.

Examples:

```python
from vflask.core.scaffolder import FieldSpec

field = FieldSpec(name="price", type="decimal")
print(field.sqlalchemy_type)
# db.Numeric(10, 2)
```

Supported type mappings include:

- `string` → `db.String(255)`
- `text` → `db.Text`
- `integer` / `int` → `db.Integer`
- `float` → `db.Float`
- `decimal` → `db.Numeric(10, 2)`
- `boolean` / `bool` → `db.Boolean`
- `date` → `db.Date`
- `datetime` → `db.DateTime`
- `json` → `db.JSON`
- `uuid` → `db.String(36)`

## 4. Mechanics of the scaffolder

### Project scaffolding flow

`ProjectScaffolder.render_project()` does the following:

1. validates the project name
2. creates the project directory
3. loads the Jinja2 templates from `vflask/templates`
4. renders each template into the generated app
5. writes core files such as:
   - `app/__init__.py`
   - `app/config.py`
   - `app/extensions.py`
   - `app/base.py`
   - `app/shared/models.py`
   - `app/modules/__init__.py`
   - `requirements.txt`
   - `docker-compose.yml`
   - `.env.example`
6. marks generated shell scripts executable

The project is generated from template files stored in:

- `vflask/templates/project/...`
- `vflask/templates/module/...`

This keeps the generated output deterministic and easy to extend.

### Module generation flow

`ModuleScaffolder.create_module()` does the following:

1. normalizes the module name to a safe Python identifier
2. creates the module folder under `app/modules`
3. builds a module metadata context with:
   - class names
   - table names
   - URL prefix
   - field definitions
   - roles
4. renders template files for:
   - `__init__.py`
   - `models.py`
   - `service.py`
   - `handlers.py`
   - `routes.py`
   - `docs.md`
   - `test_module.py`

### Why the system is structured this way

The design intentionally separates:

- project generation
- module generation
- file watching
- documentation generation

This makes it easy to add new template conventions or extend the generated project structure without rewriting the whole tool.

## 5. Generated project behavior and conventions

The generated project is intentionally opinionated and production-minded.

### App factory pattern

Generated apps use a Flask app factory:

```python
from app import create_app
app = create_app()
```

This is great for tests, multiple configs, and environment-specific startup behavior.

### PostgreSQL by default

The generated `requirements.txt` includes:

```text
Flask==3.1.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.7
Flask-JWT-Extended==4.7.1
Flask-Cors==5.0.0
psycopg[binary]==3.3.6
```

The default database URL uses PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/app
```

The generated `docker-compose.yml` includes:

- Postgres service on port `5432`
- Redis service on port `6379`

### Redis and environment config

The generated project ships with `.env.example` containing variables like:

```env
FLASK_APP=app:create_app
FLASK_DEBUG=1
SECRET_KEY=changeme
DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/app
JWT_SECRET_KEY=super-secret
REDIS_URL=redis://localhost:6379/0
PORT=5000
```

These values are intended for local development and container-based infrastructure.

### JWT + RBAC defaults

The generated app includes:

- `JWTManager`
- `Role` model
- `User` model
- `user_roles` association table
- `RBACService` helpers

This gives generated projects a base security layer with role assignment and check utilities.

### Shared utilities

The generated project creates shared convenience code:

- `app/base.py` for API helpers and decorators
- `app/shared/models.py` for role and user primitives
- `app/shared/mixins.py` for timestamp and soft-delete behavior

The decorators support patterns such as:

```python
@auth_required
def profile():
    ...

@role_required("admin")
def admin_only():
    ...
```

### Module system

Every generated module includes:

- `models.py`
- `service.py`
- `handlers.py`
- `routes.py`
- `docs.md`
- `test_module.py`

The `app/modules/__init__.py` loader discovers subfolders and registers route modules automatically.

### Docs generation and watcher

The watcher monitors `app/modules/**/handlers.py` and regenerates module docs using `DocGenerator` when handlers change.

This supports a low-friction workflow in which endpoints and business logic can be changed quickly while documentation stays in sync.

## 6. Local workflow for the repo itself

This repository also includes root-level helper scripts for local development and release flow:

```bash
./scripts/start.sh
./scripts/help.sh
./scripts/push.sh "feat: add module generator"
```

These are meant to keep the tool’s own working flow simple:

- `start.sh` sets up the local venv, installs the package, and shows CLI help
- `help.sh` prints the minimal command list
- `push.sh` stages, commits, and pushes changes

## 7. Publishing to PyPI

The project includes a GitHub Action for publishing to PyPI on repository pushes and manual workflow dispatch:

```yaml
# .github/workflows/publish.yml
```

The normal release flow is:

```bash
git add .
git commit -m "release: v0.1.0"
git push origin main
git tag v0.1.0
git push origin v0.1.0
```

This triggers the GitHub Action, which builds the package and publishes it through PyPI Trusted Publishing.

## 8. Typical development workflow

A typical vflask workflow looks like this:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .

vflask new myapp
cd myapp
vflask module create sales -f name:string:required -f amount:float -f status:string:index -r admin -r editor
vflask watch --project-root .
```

Then in the generated project:

```bash
./scripts/start.sh
```

The result is a generated Flask app that already includes a practical foundation for:

- Postgres-backed data models
- JWT authentication
- role checks and RBAC patterns
- module-based organization
- local Docker-based database services
- doc generation and watch-driven iteration

## 9. Summary

vflask combines two useful layers:

- a Python scaffolding library with explicit generation hooks
- a CLI that turns those hooks into working Flask apps and modules

It is intended for developers who want a structured, semantically typed, Django-like starter while still staying close to the Flask ecosystem and Python code they can customize directly.
