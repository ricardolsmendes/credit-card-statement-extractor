# Data Model: Python Project Setup

**Feature**: `001-python-project-setup`  
**Date**: 2026-04-11

## Overview

This feature has no runtime data model. It establishes the structural and configuration scaffolding of the project. The "entities" here are the filesystem artefacts and configuration schema.

## Filesystem Entities

### `src/` Directory

- **What it is**: Root of all application source code
- **Required contents**: One or more Python packages (directories with `__init__.py`) or modules (`.py` files)
- **Constraints**:
  - No test files (`test_*.py`, `*_test.py`) may reside here
  - Must be declared in `pyproject.toml` for packaging

### `tests/` Directory

- **What it is**: Root of all test code
- **Required contents**: Test modules following pytest naming conventions (`test_*.py`)
- **Constraints**:
  - No application business logic
  - May contain `conftest.py` for shared fixtures
  - Sub-directories allowed (e.g., `tests/unit/`, `tests/integration/`)

### `pyproject.toml`

- **What it is**: Single source of project configuration
- **Mandatory fields**:
  - `[build-system].requires` — build backend dependency list
  - `[build-system].build-backend` — build backend entry point
  - `[project].name` — package name
  - `[project].version` — version string
  - `[project].requires-python` — minimum Python version
- **Optional but expected fields**:
  - `[project].description`
  - `[project].dependencies` — runtime dependencies list
  - `[tool.pytest.ini_options]` — test runner configuration
  - `[tool.ruff]` — linter/formatter configuration
  - `[tool.hatch.build.targets.wheel]` — package discovery for build

## Configuration Schema (pyproject.toml)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "<project-name>"          # string, kebab-case
version = "<semver>"              # string, e.g. "0.1.0"
description = "<short desc>"     # string
requires-python = ">=3.11"       # version specifier
dependencies = []                 # list of PEP 508 dependency strings

[tool.hatch.build.targets.wheel]
packages = ["src/<package_name>"] # list of package paths under src/

[tool.pytest.ini_options]
pythonpath = ["src"]              # adds src/ to sys.path at test time
testpaths = ["tests"]             # restricts discovery to tests/

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "W"]    # pycodestyle, pyflakes, isort, warnings

[tool.ruff.format]
quote-style = "double"
```

## State / Lifecycle

Configuration is static — it is set during project initialisation and evolves incrementally as dependencies and tools are added. There are no state transitions at runtime.
