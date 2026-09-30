# vflask

### A practical foundation for Flask APIs

vflask generates ordinary Flask and SQLAlchemy code with a clear application structure, typed CRUD modules, authentication, migrations, tests, API documentation, and a deployable container. You keep control of the code and can change the architecture as your product grows.

`Python 3.11+` · `Flask 3` · `SQLAlchemy` · `PostgreSQL` · `Alembic`

---

## Why vflask

Flask is a strong choice when you want explicit control over request handling, dependencies, and service boundaries. vflask removes repetitive setup without hiding Flask behind a new runtime abstraction.

Choose it when you want to:

- Start with an app factory, configuration, auth, database, and test structure already connected.
- Generate consistent CRUD modules from field definitions instead of repeating model/route boilerplate.
- Keep OpenAPI documentation and focused tests beside the generated feature.
- Adopt provider interfaces and a CI/deployment baseline while retaining the option to replace them.

### When it may not fit

Choose another starting point if you need a batteries-included admin framework, a managed hosting platform, or an async-first application. The scaffold gives you service adapters, not ready-made payment, upload, or background-job products. You decide the business rules, cloud resources, and production operations.

## Quick start

Install the CLI and generate a project:

```bash
python -m pip install vflask
vflask new bookstore
cd bookstore
```

Add a feature:

```bash
vflask module create products \
  -f name:string:required \
  -f price:decimal:required \
  -f sku:string:unique \
  -r admin -r editor
```

Run the application through the CLI:

```bash
vflask run
```

`vflask run` creates `.env` from `.env.example` if needed, starts healthy local Postgres and Redis services with Docker Compose, applies generated Alembic revisions, creates missing tables and default roles, then launches Flask at `http://127.0.0.1:5000`. Use `vflask run --no-services` when connecting to services you manage yourself. Run `vflask run --help` for host and port options.

Check the API and tests:

```text
Swagger UI   http://127.0.0.1:5000/api/v1/docs
OpenAPI      http://127.0.0.1:5000/api/v1/openapi.json
```

```bash
pytest -q
```

## Architecture

```text
app/
  auth/          JWT auth and Google OAuth routes
  base/          API responses, JSON types, query filters, OpenAPI reflection
  integrations/  payment, storage, mail, and OAuth provider adapters
  shared/        users, roles, timestamps, and RBAC
  modules/       generated models, services, handlers, routes, docs, and tests
migrations/      Alembic environment, revisions, and version history
tests/           application-level pytest fixtures
.github/         CI and EC2 deployment workflows
Dockerfile       non-root Gunicorn runtime
docker-compose.yml app + PostgreSQL + Redis development network
```

Generated modules are regular Python packages registered as Flask blueprints. Services contain database operations, handlers validate API input, and model serializers define the returned fields. Swagger reflects registered models and their serialized data.

## Capabilities

| Area        | Included scaffold                                                                           |
| ----------- | ------------------------------------------------------------------------------------------- |
| Application | App factory, configuration, SQLAlchemy, Flask-Migrate, JWT, RBAC                            |
| Modules     | Typed CRUD structure, per-module docs and tests, generated table migration                  |
| Data        | PostgreSQL defaults, SQLite-friendly tests, automatic migration and missing-table bootstrap |
| API         | Reflected OpenAPI 3, Swagger UI, paginated list endpoints (limit up to 100)                 |
| Identity    | Signup/login, token verification/refresh, password recovery, profile, Google OAuth          |
| Providers   | Flutterwave, S3 or Cloudinary, SMTP or SES; replaceable protocols                           |
| Delivery    | Strict Pyright check, pytest, Compose smoke test, Docker image, EC2 workflow                |

### Field definitions

Supported types: `string`, `text`, `integer`, `float`, `decimal`, `boolean`, `date`, `datetime`, `json`, and `uuid`. Flags: `required`, `unique`, `index`, `nullable`, and `default=value`.

```text
name:string:required
sku:string:unique
price:decimal:required
metadata:json
```

## Database lifecycle

Each newly generated module includes an Alembic revision linked to the current migration head. `vflask run` applies those revisions before starting the app, then runs an idempotent bootstrap for missing tables and default roles. Container startup follows the same sequence. No known-password admin user is created.

For hand-edited model changes or data migrations, generate and review a revision:

```bash
APP_ENV=development flask --app app:create_app db migrate -m "describe schema change"
APP_ENV=development flask --app app:create_app db upgrade
```

Commit the revision with the model change. `db.create_all()` only creates absent tables; it does not alter existing tables, so column changes and renames belong in Alembic migrations.

## Auth and API docs

Auth routes are under `/api/v1/auth`. Google sign-in is an authorization-code flow: configure `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and the exact public `GOOGLE_REDIRECT_URI`; request `/api/v1/auth/google/authorization-url`; redirect the client to its returned URL; then send Google's `code` and signed `state` to `/api/v1/auth/google/callback`. The server exchanges the code, requires a verified email, and returns app JWTs.

OpenAPI is available at `/api/v1/openapi.json`; Swagger UI is at `/api/v1/docs`. Per-module Markdown remains available at `/api/v1/docs/<module>`. Generated list routes require positive `pagination.page` and `pagination.limit`; the maximum limit is 100.

## Providers

Use `get_payment_provider()`, `get_storage_provider()`, and `get_mailer()` from `app.integrations`.

| Service | Default     | Alternatives                          | Selection                                     |
| ------- | ----------- | ------------------------------------- | --------------------------------------------- |
| Payment | Flutterwave | Custom`PaymentProvider`               | `PAYMENT_PROVIDER` / `PAYMENT_PROVIDER_CLASS` |
| Storage | S3          | Cloudinary or custom`StorageProvider` | `STORAGE_PROVIDER` / `STORAGE_PROVIDER_CLASS` |
| Email   | SMTP        | Amazon SES or custom`MailProvider`    | `MAIL_PROVIDER` / `MAIL_PROVIDER_CLASS`       |

Provider credentials are environment-driven. For production S3 and SES, attach an IAM role to EC2 instead of storing AWS access keys. Scope S3 access to the required bucket/prefix and SES access to the verified sender identity. Add payment verification, upload authorization, and other product rules in your own service layer; the scaffold does not expose generic provider endpoints.

## Deployment

The generated Docker image runs Gunicorn as a non-root user. GitHub Actions runs tests and strict Pyright, starts app/Postgres/Redis with Compose, and probes the app health endpoint. On pushes to `main`, the deployment workflow publishes to Docker Hub, applies committed migrations, and replaces the EC2 container.

Configure repository secrets:

```text
DOCKER_PAT       DOCKER_USERNAME
EC2_HOST         EC2_USER
EC2_SSH_KEY      PROJECT_NAME
ENV_FILE
```

`ENV_FILE` is the complete production environment file. Use independent signing keys of at least 32 characters and a reachable production `DATABASE_URL`. Production startup rejects placeholder secrets and localhost database URLs. Install Docker Engine on EC2, grant the deploy user Docker access, and put a TLS-terminating reverse proxy in front of port 5000. The deployment baseline does not provision a production database or cloud IAM resources.

## CLI reference

```bash
vflask new <project>                # Create a project
vflask module create <name> -f ... # Create a module and migration
vflask run                          # Prepare local services and run Flask
vflask watch --project-root .        # Regenerate module docs on changes
```
