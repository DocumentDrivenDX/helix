---
title: "Python + uv"
slug: python-uv
generated: true
aliases:
  - /reference/glossary/concerns/python-uv
---

**Category:** Tech Stack · **Areas:** all

## Description

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
- **Configuration**: `pydantic-settings` (TOML file sources plus environment) — one central typed `Settings` class; NOT bare `os.environ`/`os.getenv`, NOT `python-dotenv` called directly, NOT `dynaconf`/`configparser`

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
- Config is layered by owner per `twelve-factor`: ops-injected values (env vars, mounted files, secret manager) over a committed `config/<env>.toml` over committed defaults (field defaults plus `config/default.toml`), wired via `settings_customise_sources`; ops-owned keys (hosts, credentials) are required fields with no default and never appear in committed files
- Real environment variables take precedence over files; `.env` is a local-development convenience only, git-ignored, with a committed `.env.example` listing every variable (no secrets in it)

## When to use

Python projects that benefit from fast dependency resolution and reproducible
environments. Good for data services, APIs, ML pipelines, CLI tools, and
libraries. uv is the single tool for venv creation, dependency resolution,
and script running.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: Python 3.12+ + uv (ruff, pyright, pytest) as the language-runtime
- TD: pyproject.toml layout, dependency-group conventions, branch-coverage floor, central `Settings` class and its config-key contract (owner and source per key)

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

## Requirements (Frame activity)
- Specify minimum Python version (3.12+ preferred)
- Inventory the configuration the system needs (endpoints, credentials, feature flags) and which are secrets
- Identify whether the project is a library (published) or an application (not published)
- If ML/GPU dependencies exist, plan for `[tool.uv.sources]` with custom package indexes

## Design
- One `pyproject.toml` per project (or per package in a workspace)
- Library projects: use `hatchling` build backend with `uv-dynamic-versioning` for git-tag-based versions
- Application projects: `[tool.uv] package = false` (no build artifact needed)
- Organize source under `src/<package_name>/` layout
- Use `pydantic` v2 for data validation
- Centralize configuration in one `pydantic-settings` `BaseSettings` subclass; group related settings with nested models and an `env_nested_delimiter` / `env_prefix` rather than scattering reads
- Use `SecretStr` for credentials and `AnyUrl`/`PostgresDsn`-style types for endpoints; validate at startup so bad config fails fast
- Source precedence: init args > environment variables / secret files > `.env` (dev only) > `config/<env>.toml` > `config/default.toml` > field defaults (two `TomlConfigSettingsSource` instances via `settings_customise_sources`, returning `(init, env, file_secret, dotenv, toml_env, toml_default)`); ops-owned keys are required fields, dev-owned keys carry defaults; production relies on real env vars or the platform secret manager
- `settings_customise_sources` reads `APP_ENV` via `os.environ.get` once, before constructing `toml_env`, to pick `config/<env>.toml`; that one read is the sanctioned exception to "no `os.environ`/`os.getenv` outside the settings module"
- Commit `.env.example`; git-ignore `.env`
- Use `typer` + `rich` for CLI interfaces

## Implementation
- Create/sync environment: `uv sync` (creates `.venv` automatically)
- Run scripts: `uv run python ...` or `uv run pytest`
- Add dependencies: `uv add <pkg>` (not `pip install`)
- Add dev dependencies: `uv add --dev <pkg>` or to `[dependency-groups] dev`
- Read configuration only through the central `Settings` object, built once at the entrypoint and injected; never `os.getenv`
- Tests construct `Settings(...)` directly (or via `monkeypatch.setenv`) — never depend on a developer's `.env`
- Type annotations: all public functions and methods must have type annotations
- Avoid `Any` — use `pyright` targeted `# type: ignore` with comment when unavoidable
- Use `TYPE_CHECKING` guard for import-only type imports

## Testing
- Framework: `pytest`
- Run: `uv run pytest`
- Property-based: `hypothesis` for data invariants and input space exploration
- Mocking: `pytest-mock` (not `unittest.mock` directly)
- Coverage: `pytest-cov` with branch coverage; set `fail_under` in `[tool.coverage.report]`
- Test markers: `acceptance`, `contract`, `slow`, `fast` — use `--strict-markers`
- Filter known third-party deprecation warnings in `[tool.pytest.ini_options] filterwarnings`

## Quality Gates (pre-commit / CI)
- `ruff check .` — lint
- `ruff format --check .` — format
- `pyright` — type check
- `uv run pytest --cov` — tests with coverage
- `pre-commit run --all-files` for the full gate
- Complexity, statement, argument, and public-method ceilings, a file-size cap, and pyright `strict` on application code, per `code-shape-ceilings` (strict defaults for new projects; ceilings only go down)
- Reject `os.environ`/`os.getenv` outside the settings module (ruff `TID251` banned-api on `os.getenv`/`os.environ`, ignored per-file for the settings module)

## Dependency Management
- `uv add <pkg>` / `uv add --dev <pkg>`
- Custom indexes: declare in `[tool.uv.sources]` and `[[tool.uv.index]]`
- Lock file: `uv.lock` committed
- Do not commit `.venv/` or use system Python
