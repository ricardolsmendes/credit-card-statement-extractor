# Quickstart: Python Project Setup

**Feature**: `001-python-project-setup`  
**Date**: 2026-04-11

## What Gets Created

```text
credit-card-statement-extractor/
├── pyproject.toml               # Single project configuration file
├── uv.lock                      # Locked dependency versions (committed)
├── src/
│   └── credit_card_statement_extractor/
│       └── __init__.py          # Application package root
└── tests/
    └── __init__.py              # Makes tests a package (optional but conventional)
```

## Prerequisites

Install `uv` (the project's only required tool):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## After Cloning

Install all dependencies and create the virtual environment:

```bash
uv sync --all-extras
```

`uv` manages the `.venv` directory automatically — do not create or activate it manually.

## Run Tests

```bash
uv run pytest
```

## Lint and Format

```bash
uv run ruff check .
uv run ruff format .
```

## Adding Application Code

Place new modules under `src/credit_card_statement_extractor/`:

```text
src/credit_card_statement_extractor/
├── __init__.py
├── parser.py        # example module
└── models.py        # example module
```

## Adding Tests

Place test files under `tests/`:

```text
tests/
├── __init__.py
├── test_parser.py   # tests for src/.../parser.py
└── test_models.py
```

Test files must be named `test_*.py` or `*_test.py` to be auto-discovered by pytest.

## Adding a Dependency

```bash
uv add <package-name>
```

For development-only dependencies:

```bash
uv add --optional dev <package-name>
```

## Key Rules

- All configuration goes in `pyproject.toml`. Do not create `setup.py`, `setup.cfg`, `tox.ini`, `.flake8`, or separate `requirements.txt` files.
- Use `uv` for all dependency operations — never `pip` directly.
- Commit `uv.lock` to version control for reproducible installs.
