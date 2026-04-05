# Practices: Python + uv

## Project Setup

- Use `pyproject.toml` with `[project]` table
- Pin Python version: `.python-version`
- Lock file: `uv.lock` (committed to git)

## Type Checking

- Use `mypy --strict` or `pyright` in strict mode
- All public functions must have type annotations
- Use `typing.Protocol` for interfaces, not ABC

## Linting & Formatting

- Linter: `ruff check`
- Formatter: `ruff format`
- Config in `pyproject.toml` under `[tool.ruff]`

## Testing

- Framework: `pytest`
- Use `pytest-cov` for coverage
- Fake data with `faker` or `factory_boy`, not static fixtures
- Use `unittest.mock.patch` sparingly — prefer dependency injection

## Dependencies

- Add with `uv add`, not `pip install`
- Dev dependencies: `uv add --dev`
- Scripts: define in `pyproject.toml` under `[project.scripts]`
