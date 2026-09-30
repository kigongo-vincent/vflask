# vflask

A typed Flask scaffolding tool that creates Django-like project shells with module generators, role-based access controls, file watching, and Postgres-ready configuration.

## Install

```bash
python3 -m pip install -e .
```

## Usage

```bash
vflask --help
vflask new myapp
cd myapp
vflask module create sales -f name:string -f amount:float -f status:string:index -r admin -r editor
```

## Local workflow

```bash
./scripts/start.sh
./scripts/help.sh
./scripts/push.sh "feat: add module generator"
```

This keeps the project workflow to a single entry script, a single push script, and a quick help command.

## Release to PyPI

This repo includes a GitHub Action that publishes the package to PyPI when a version tag is pushed.

```bash
git tag v0.1.0
git push origin v0.1.0
```

The workflow in `.github/workflows/publish.yml` builds the package and publishes it through PyPI Trusted Publishing.

## Production bundle

```bash
cd myapp
./scripts/build.sh
```

This creates a compressed production bundle in the `dist/` folder.
