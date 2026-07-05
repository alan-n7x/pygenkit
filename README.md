# PyGenesis

Professional Python project generator -- **PyPI**, **APT**, and **Launchpad** ready.

Inspect existing Python projects, validate version consistency and CI/CD security, and
generate GitHub Actions pipelines, Dockerfiles, and deploy configs.

## Installation

```bash
pip install pygenesis
```

Or via `uv`:

```bash
uv tool install pygenesis
```

## Quick Start

```bash
# Initialize config in your project
pygenesis init my-app

# Inspect project structure
pygenesis inspect

# Validate versions, workflows, security
pygenesis validate

# Generate CI/CD pipelines, Docker, deploy configs
pygenesis generate

# Check system requirements
pygenesis doctor
```

## Commands

| Command         | Description                                    |
|-----------------|------------------------------------------------|
| `init`          | Create `pygenesis.toml` in an existing project |
| `inspect`       | Analyze project structure, versions, metadata  |
| `validate`      | Check version consistency, workflows, security |
| `generate`      | Generate CI/CD, Docker, and deploy files       |
| `release-check` | Verify release readiness (coming soon)         |
| `doctor`        | Check system for required tools                |

## Usage

```bash
# Create config
pygenesis init my-project

# Inspect project
pygenesis inspect

# Validate
pygenesis validate

# Generate GitHub Actions CI/CD pipelines
pygenesis generate

# Dry-run to preview without writing
pygenesis generate --dry-run

# Overwrite existing files
pygenesis generate --force

# Enable Docker + deploy in config, then generate:
#   [docker]
#   enabled = true
#   base_image = "3.12"
#   port = 8000
#
#   [deploy]
#   enabled = true
#   fly = true
#   heroku = true
#   railway = true
```

## Inspect

Scans your project and reports:

- Project name, version, module
- Build backend (setuptools, hatchling, poetry, etc.)
- Python version requirement
- License type (MIT, Apache, GPL, etc.)
- Version consistency between `pyproject.toml`, `__init__.py`, `debian/changelog`, and git tags
- CI/CD workflow detection
- Debian packaging status

## Validate

Runs three categories of checks:

- **Version**: consistency across `pyproject.toml`, `__init__.py`, `debian/changelog`, git tags
- **Workflow**: YAML validity, missing metadata, outdated actions (`checkout@v3`), SHA pin warnings, script injection
- **Security**: missing permissions blocks, hardcoded secrets, PyPI publish without protected environment

## Generate

Generates files from Jinja2 templates based on `pygenesis.toml`:

### GitHub Actions

| File                   | Description                               |
|------------------------|-------------------------------------------|
| `.github/workflows/ci.yml` | Ruff lint, MyPy type-check, Pytest      |
| `.github/workflows/release.yml` | Build wheel, create GitHub Release |
| `.github/workflows/publish-pypi.yml` | Trusted PyPI publishing     |
| `.github/workflows/publish-launchpad.yml` | dput to Launchpad PPA   |

### Docker

| File                 | Description            |
|----------------------|------------------------|
| `Dockerfile`         | Multi-stage build      |
| `docker-compose.yml` | Service configuration  |

### Deploy

| File            | Platform |
|-----------------|----------|
| `fly.toml`      | Fly.io   |
| `Procfile`      | Heroku   |
| `railway.json`  | Railway  |

## Configuration (`pygenesis.toml`)

```toml
[project]
name = "my-app"
version = "0.1.0"
extras = ""

[ci]
python_versions = ["3.12", "3.13"]
runner = "ubuntu-latest"
lint = true
type_check = true

[release]
branch = "main"
tag_prefix = "v"
changelog = "CHANGELOG.md"

[pypi]
enabled = true
environment = "pypi"
trusted_publishing = true

[debian]
enabled = true
email = ""
name = ""
owner = ""
ppa = "tools"
distributions = ["noble"]
revision = "1"

[github]
ci = true
release = true
publish_pypi = true
publish_launchpad = true

[docker]
enabled = false
base_image = "3.12"
port = 8000
volumes = []

[deploy]
enabled = false
fly = true
heroku = true
railway = true
primary_region = "iad"
port = 8000
memory = "512mb"
cpu_kind = "shared"
cpus = 1
```

## Doctor

```bash
pygenesis doctor
```

Checks for:
- Python 3.12+
- Git
- GitHub CLI (gh)
- GPG
- dput
- debhelper
- twine
- build

## Architecture

```
src/pygenesis/
├── cli/              # CLI commands (Typer)
│   └── commands/     # init, inspect, validate, generate, release-check, doctor
├── generators/       # GitHub Actions, Docker, Deploy generators
│   ├── base.py       # Base generator with RenderEngine
│   ├── github_actions.py
│   ├── docker.py
│   ├── deploy.py
│   └── orchestrator.py
├── inspector/        # Read and analyze existing projects
│   ├── api.py        # Main inspect_project()
│   ├── debian.py     # Debian packaging inspection
│   ├── detect.py     # Module, tests, license, version detection
│   ├── git.py        # Git remote, tags
│   └── pyproject.py  # pyproject.toml parsing
├── models/           # Data models (dataclasses)
│   ├── config.py     # PyGenesisConfig and sub-configs
│   └── inspection.py # ProjectInspection and sub-inspections
├── render/           # Jinja2 rendering engine
├── templates/        # Jinja2 templates for generation
│   ├── github/workflows/   # CI, release, PyPI, Launchpad workflows
│   ├── docker/             # Dockerfile, docker-compose
│   └── deploy/             # Fly.io, Heroku, Railway configs
├── utils/            # File utilities, template filters
└── validators/       # Version, workflow, security validators
    ├── api.py
    ├── version.py
    ├── workflow.py
    └── security.py
```

## Requirements

- Python 3.12+

## License

MIT
