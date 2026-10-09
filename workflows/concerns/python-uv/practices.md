# Practices: python-uv

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
