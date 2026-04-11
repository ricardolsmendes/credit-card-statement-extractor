# Research: Python Project Setup

**Feature**: `001-python-project-setup`  
**Date**: 2026-04-11

## Decision Log

### Build Backend

**Decision**: Hatchling (`hatchling`)  
**Rationale**: De facto standard for modern Python projects (2025–2026). Zero-dependency, excellent src-layout support, actively maintained, used by CPython ecosystem tools. No legacy baggage unlike setuptools.  
**Alternatives considered**:
- `setuptools` — requires extra configuration for src-layout (`packages = find:`, `package_dir`); still dominant in legacy projects but adds friction
- `flit-core` — simpler but less feature-complete; best for pure-Python packages with no build-time steps
- `pdm-backend` — ties the project to the PDM workflow; avoids to keep toolchain choice open

### Package Discovery

**Decision**: Explicit `[tool.hatch.build.targets.wheel] packages = ["src/<package-name>"]`  
**Rationale**: Explicit is better than implicit (Zen of Python). Makes the package boundary unambiguous. Hatchling supports auto-discovery but explicit declaration is safer and clearer for contributors.

### Pytest Import Resolution (src-layout)

**Decision**: `[tool.pytest.ini_options] pythonpath = ["src"]`  
**Rationale**: The standard pytest ≥ 7.0 mechanism for src-layouts. Adds `src/` to `sys.path` at test time so application packages are importable without installation. No `conftest.py` path hacking or `pip install -e .` required for basic test runs.

### Linter / Formatter

**Decision**: Ruff (both lint and format)  
**Rationale**: Mandated by the project constitution. Single tool replaces flake8 + isort + black. Configured entirely in `pyproject.toml` under `[tool.ruff]`.

### Python Version

**Decision**: Require Python ≥ 3.11  
**Rationale**: Python 3.11 is the oldest actively maintained release as of 2026. Provides `tomllib` in stdlib (useful for parsing config), improved error messages, and performance improvements. Aligns with "modern Python" intent.

### Existing Project Files

No pre-existing `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements.txt`, or `Pipfile` found. Greenfield setup — no migration required.
