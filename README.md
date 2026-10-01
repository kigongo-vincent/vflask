# vflask

A production-minded Flask scaffolder for teams that want cleaner architecture, faster module generation, and safer defaults from day one.

## Why vflask

vflask helps you go from an empty Flask app to a structured product foundation without hiding Flask behind a heavy abstraction layer.

It gives you:

- app factory + configuration defaults
- typed module generation for CRUD features
- JWT auth and Google OAuth scaffolding
- Alembic migrations and schema tracking
- tests, docs, Docker support, and deployment workflows
- sane defaults for local development and production readiness

## Quick start

```bash
python -m pip install vflask
vflask new bookstore
cd bookstore
```

Create a module:

```bash
vflask module create products \
  -f name:string:required \
  -f price:decimal:required \
  -f sku:string:unique \
  -r admin -r editor
```

Run the app:

```bash
vflask run
```

## Project structure

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
```

## CLI reference

| Command | Purpose |
| --- | --- |
| `vflask new <project>` | Create a fresh project scaffold |
| `vflask module create <name> -f ...` | Generate a typed business module |
| `vflask run` | Start the app with local services by default |
| `vflask run --no-services` | Run without Compose-managed Postgres/Redis |
| `vflask watch --project-root .` | Regenerate docs when modules change |

## Module field system

Supported field types:

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

Supported flags:

- `required`
- `unique`
- `index`
- `nullable`
- `default=value`

Example:

```text
name:string:required
sku:string:unique
price:decimal:required
metadata:json
```

## Testing and deployment

```bash
pytest -q
python -m build
python -m twine check dist/*
```

Release behavior:

- default package version starts at `1.0.0`
- tagged releases like `v1.2.3` work as semantic version updates
- first publish creates a missing PyPI project
- repeated uploads of the same version are skipped safely

## Common edge cases

| Scenario | Recommended approach |
| --- | --- |
| Missing env vars | Copy `.env.example` to `.env` and fill in values |
| Schema drift | Use Alembic migrations instead of editing DB schema by hand |
| OAuth errors | Verify the exact public `GOOGLE_REDIRECT_URI` |
| Local DB startup race | Wait for Postgres and Redis readiness or use `--no-services` |
| Secret leaks | Keep secrets in CI/CD or secret managers, not source control |

## Production checklist

- keep secrets in environment variables or a secret manager
- use managed Postgres in production
- run tests before every release
- use migrations for schema changes
- use Docker and health checks for deployability
- version packages with semantic versioning

## Terminal help

```bash
./scripts/help.sh
```

## Environment variables

Use these values in production or local setup when enabling provider integrations:

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI`
- `EC2_SSH_KEY`

This project is designed to help teams build enterprise-ready Flask apps with a clean architecture, predictable CRUD generation, and safe production defaults.
