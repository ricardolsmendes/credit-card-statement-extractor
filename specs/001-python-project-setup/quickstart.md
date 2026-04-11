# Quickstart: Python Project Setup

**Feature**: `001-python-project-setup`  
**Date**: 2026-04-11

## What Gets Created

```text
credit-card-statement-extractor/
├── pyproject.toml               # Single project configuration file
├── src/
│   └── credit_card_statement_extractor/
│       └── __init__.py          # Application package root
└── tests/
    └── __init__.py              # Makes tests a package (optional but conventional)
```

## After Implementation

### Install in editable mode (optional, for IDE support)
```bash
pip install -e .
```

### Run tests
```bash
pytest
```

### Lint and format
```bash
ruff check .
ruff format .
```

## Adding Application Code

Place new modules under `src/credit_card_statement_extractor/`:
```bash
src/credit_card_statement_extractor/
├── __init__.py
├── parser.py        # example module
└── models.py        # example module
```

## Adding Tests

Place test files under `tests/`:
```bash
tests/
├── __init__.py
├── test_parser.py   # tests for src/.../parser.py
└── test_models.py
```

Test files must be named `test_*.py` or `*_test.py` to be auto-discovered by pytest.

## Key Rule

All configuration goes in `pyproject.toml`. Do not create `setup.py`, `setup.cfg`, `tox.ini`, `.flake8`, or separate `requirements.txt` files.
