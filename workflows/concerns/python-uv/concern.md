# Concern: Python + uv

## Category
tech-stack

## Areas
all

## Slot
language-runtime

## Components

- **Language**: Python 3.12+
- **Package manager**: uv — NOT pip, NOT poetry, NOT conda
- **Virtual environment**: uv-managed (`.venv` via `uv sync`)
- **Build backend**: `hatchling` with `uv-dynamic-versioning` for versioned packages
- **Linter**: `ruff` — NOT flake8, NOT pylint
- **Type checker**: `pyright` — NOT mypy
- **Test framework**: `pytest` with `pytest-cov`
- **Property-based testing**: `hypothesis`
- **Configuration**: `pydantic-settings` — one central typed `Settings` class; NOT bare `os.environ`/`os.getenv`, NOT `python-dotenv` called directly, NOT `dynaconf`/`configparser`

## Constraints

- All code must pass `pyright` type checking
- All code must pass `ruff check` and `ruff format --check`
- Use `pyproject.toml` for all project metadata (not `setup.py`, not `setup.cfg`)
- Pin Python version in `.python-version`
- All dependencies in `[project.dependencies]` or `[dependency-groups]` (dev); no `requirements.txt`
- Use `[tool.uv.sources]` for custom package indexes (e.g., PyTorch CUDA wheels)
- Tests in `tests/` directory; pytest markers for test categories (acceptance, contract, slow, fast)
- Branch coverage enforced via `pytest-cov` with `fail_under`
- All configuration is declared in one central `pydantic-settings` `BaseSettings` subclass (single module, e.g. `src/<package>/settings.py`); every setting is a typed field with a default or is required
- Settings are instantiated once at the composition root (app/CLI entrypoint) and passed in; no `os.environ`/`os.getenv` reads and no module-level settings singletons elsewhere in the codebase
- Secrets use `SecretStr`; missing or invalid config fails at startup, not at first use
- Real environment variables take precedence; `.env` is a local-development convenience only, git-ignored, with a committed `.env.example` listing every variable (no secrets in it)

## When to use

Python projects that benefit from fast dependency resolution and reproducible
environments. Good for data services, APIs, ML pipelines, CLI tools, and
libraries. uv is the single tool for venv creation, dependency resolution,
and script running.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: Python 3.12+ + uv (ruff, pyright, pytest) as the language-runtime
- TD: pyproject.toml layout, dependency-group conventions, branch-coverage floor, central `Settings` class and its env-var contract
