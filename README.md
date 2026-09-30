# vflask

vflask is a modern Flask framework starter built for developers who want the speed of scaffolding without losing the flexibility of raw Flask.

If you like Flask but want the structure and conventions of a more opinionated framework, vflask gives you a strong starting point: typed project generation, module-based architecture, PostgreSQL defaults, JWT auth, role-based access control, Redis support, Docker-ready setup, and a CLI that turns a feature idea into a working app in minutes.

This is the kind of framework that feels familiar to Flask developers, but removes the repetitive setup that slows teams down.

## Why developers choose vflask

- Flask-first, not framework-lock-in: you still write Flask code, but with a stronger project skeleton
- Faster prototyping: generate a production-like app structure in one command
- Safer defaults: PostgreSQL, env config, JWT auth, RBAC, Docker Compose included
- Easier modularity: create modules with typed fields and automatic route/service/model scaffolds
- Better team workflow: generated docs and watch mode keep module structure readable
- Less boilerplate: no need to manually wire common app patterns every time

## Install globally

```bash
python3 -m pip install vflask
```

If you want the latest unreleased version from a local checkout instead, use a venv for that workflow, but for normal end-user usage the intended install is a global pip install.

## Quick start

Create a project:

```bash
vflask new myapp
cd myapp
```

Create a module:

```bash
vflask module create sales \
  -f name:string:required \
  -f amount:float \
  -f status:string:index \
  -r admin \
  -r editor
```

Start the generated app:

```bash
./scripts/start.sh
```

Open the app and you will already have:

- a Flask app factory
- configured app extensions
- PostgreSQL connection settings
- Redis support
- a default user and role system
- a module layout with routes, handlers, and models

## What vflask generates

Every new project gives you a ready-to-use Flask application with a structure designed for real-world backend work.

### Included by default

- PostgreSQL configuration with `psycopg[binary]`
- Redis-ready environment variables
- JWT authentication setup
- role-aware access helpers
- app factory pattern
- modular project layout
- Docker Compose for local services
- module generation commands
- docs generation and watch mode

### Example generated app structure

```text
myapp/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── base.py
│   ├── shared/
│   └── modules/
├── migrations/
├── tests/
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── README.md
├── scripts/
│   ├── start.sh
│   ├── push.sh
│   └── help.sh
└── .venv/
```

## Core CLI commands

### New project

```bash
vflask new myapp
```

Creates a new Flask app scaffold in a new folder.

### Module creation

```bash
vflask module create orders \
  -f order_id:string:required \
  -f total:float \
  -f status:string:index \
  -r admin \
  -r editor
```

Generates a full module with:

- model definition
- service layer
- handlers
- routes
- docs page
- tests

### Watch mode

```bash
vflask watch --project-root .
```

Watches module changes and refreshes generated docs when handlers change.

## A real developer workflow

A typical vflask workflow looks like this:

```bash
vflask new crm
cd crm
vflask module create leads \
  -f name:string:required \
  -f email:string:unique \
  -f amount:float \
  -r admin

./scripts/start.sh
```

From there, you are operating inside a Flask project that already includes the structure most teams need but do not want to build from scratch each time.

## Typed field system

The scaffolder supports field definitions like this:

```text
name:string:required
amount:float
status:string:index
email:string:unique
created_at:datetime
```

This becomes the core of generated models and keeps your schema definitions clean and readable.

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

### Supported field flags

- `required` / `notnull` / `nonnullable`
- `unique`
- `index`
- `default=value`
- `nullable`

## Why this is useful for Flask teams

This is not just a project template. It is a practical productivity layer for Flask developers.

It helps teams do all of the following without adding a lot of framework ceremony:

- generate consistent app structure
- scaffold CRUD modules fast
- reuse role-based access patterns
- keep route/service/model organization consistent
- reduce the time spent wiring the boring parts of backend apps
- maintain cleaner project conventions across multiple services

## Built for real backend work

The generated app is not a toy app. It is structured with practical backend concerns in mind:

- Redis and PostgreSQL support
- JWT auth
- role checks for API access
- service-oriented modules
- module docs generation
- local Docker services for development

This makes vflask useful for internal tools, SaaS backends, CRUD-heavy APIs, admin apps, and operational tooling built with Flask.

## Summary

vflask is for Flask developers who want more structure, better conventions, and faster scaffolding without abandoning the simplicity and flexibility that makes Flask great.

It turns a blank Flask project into a usable, structured backend foundation in minutes — while still letting you stay close to the framework you already know.
