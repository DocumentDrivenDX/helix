# Concern: Python + uv

## Category
tech-stack

## Areas
all

## Components

- **Language**: Python 3.12+
- **Package manager**: uv (not pip, not poetry)
- **Virtual environment**: uv-managed (not conda, not pyenv)

## Constraints

- All code must pass `mypy --strict` or `pyright` type checking
- Use `pyproject.toml` for project metadata (not `setup.py`)
- Pin Python version in `.python-version`

## When to use

Python projects that benefit from fast dependency resolution and
reproducible environments. Good for data services, APIs, ML pipelines,
and CLI tools.

## ADR References
