# vflask

> Production-minded Flask scaffolding for teams building modern, maintainable apps without starting from a blank page.

<p align="center">
  <img src="https://images.pexels.com/photos/1181244/pexels-photo-1181244.jpeg?auto=compress&cs=tinysrgb&w=1400" alt="Developer team working on a product" width="100%" />
</p>

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/) [![Flask 3](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/) [![CI](https://img.shields.io/badge/CLI-vflask-FF385C)](https://pypi.org/project/vflask/)

vflask turns a blank Flask project into a structured foundation for real products. It gives teams a clean app skeleton, typed module generation, auth, RBAC, migrations, tests, deployment workflows, and a dependable local runtime from day one.

## Why teams use vflask

- Clean application structure with clear separation of concerns
- Typed CRUD module generation to reduce repetitive boilerplate
- JWT auth, OAuth, service integrations, and RBAC scaffolding
- Database migrations and safe schema evolution
- Built-in health checks, Docker support, and deployment conventions
- Better onboarding for junior engineers and more consistency for senior teams

## Quick start

```bash
python -m pip install vflask
vflask new bookstore
cd bookstore
```

Create a business module:

```bash
vflask module create products \
  -f name:string:required \
  -f price:decimal:required \
  -f sku:string:unique \
  -r admin -r editor
```

Run the application:

```bash
vflask run
```

## Full app structure

```text
app/
  auth/
  base/
  integrations/
  shared/
  modules/
  tests/
  migrations/
  Dockerfile
  docker-compose.yml
  .env.example
  scripts/
  .github/
```

## What gets generated

| Artifact | Purpose | Why it matters |
| --- | --- | --- |
| `models.py` | SQLAlchemy schema | Creates the data contract |
| `routes.py` | HTTP endpoints and blueprints | Exposes the API surface |
| `services.py` | Business logic | Keeps handlers thin and testable |
| `handlers.py` | Validation and response shaping | Reduces invalid input and duplicate logic |
| `migration.py` | Alembic revision stub | Safely tracks schema changes |
| `test_module.py` | Module-level tests | Prevents regressions early |

## Module field system

### Supported field types

- `string`
- `text`
- `integer`
- `float`
- `decimal`
- `boolean`
- `date`
- `datetime`
- `json`
- `uuid`

### Supported flags

- `required`
- `unique`
- `index`
- `nullable`
- `default=value`

### Example

```text
name:string:required
sku:string:unique
price:decimal:required
metadata:json
```

## CLI reference

| Command | Purpose |
| --- | --- |
| `vflask new <project>` | Create a new project scaffold |
| `vflask module create <name> -f ...` | Generate a typed business module |
| `vflask run` | Start the app with local services by default |
| `vflask run --no-services` | Use your own Postgres/Redis instead of Compose |
| `vflask watch --project-root .` | Regenerate docs when modules change |

## Local workflow

```bash
pytest -q
python -m build
python -m twine check dist/*
```

### Release behavior

- Default package version starts at `1.0.0`
- Tagged versions such as `v1.2.3` work as semantic releases
- First publish creates a missing PyPI project automatically
- Repeated uploads of the same version are skipped safely

## Common enterprise edge cases

| Scenario | Recommended approach |
| --- | --- |
| Missing environment variables | Copy `.env.example` to `.env` and fill in the real values |
| Database drift | Use Alembic migrations instead of editing schema by hand |
| OAuth failures | Verify the exact `GOOGLE_REDIRECT_URI` and app credentials |
| Local service startup race | Wait for Postgres and Redis readiness or use `--no-services` |
| Secret leaks | Store values in CI/CD or a secret manager, not source control |
| Duplicate package uploads | Use a valid version tag or rely on the `1.0.0` default for first release |

## Environment variables

Use these values when enabling provider integrations or deployment automation:

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI`
- `EC2_SSH_KEY`

## Production checklist

- Keep secrets in environment variables or a secret manager
- Use managed Postgres in production
- Run tests before each deployment
- Use Alembic for schema changes
- Keep Docker and health checks in the release path
- Version packages with semantic versioning

## Terminal help

```bash
./scripts/help.sh
```

## Visual landing page

For the more polished static landing page with custom SVG sections and Pexels imagery, open [docs/index.html](docs/index.html) in a browser.

---

vflask is designed to help teams build enterprise-ready Flask apps with a clean architecture, predictable CRUD generation, and safer production defaults.
