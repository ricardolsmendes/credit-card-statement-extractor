# Implementation Plan: Python Project Setup

**Branch**: `001-python-project-setup` | **Date**: 2026-04-11 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/001-python-project-setup/spec.md`

## Summary

Create the foundational Python project structure: application source code under `src/`, tests under `tests/`, and all project configuration consolidated in a single `pyproject.toml` using Hatchling as the build backend, pytest as the test runner, and Ruff as the linter/formatter.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: `hatchling` (build), `pytest` (test), `ruff` (lint/format)  
**Storage**: N/A  
**Testing**: pytest  
**Target Platform**: Cross-platform developer workstation  
**Project Type**: CLI tool  
**Performance Goals**: Per constitution — single statement extraction < 2s (not affected by this feature)  
**Constraints**: src-layout; all config in `pyproject.toml`; no legacy config files  
**Scale/Scope**: Single-package project

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| Code quality / Ruff enforces style | Pass | Ruff configured in `pyproject.toml` |
| Test-first: tests structure before app code | Pass | `tests/` established as first-class structure |
| CLI contract unchanged | Pass | No CLI changes in this feature |
| No speculative features | Pass | Minimal scaffolding only |
| Dependencies are liabilities — add only essential | Pass | hatchling, pytest, ruff are all essential |
| No dead code / TODO-as-code | Pass | No implementation code in this feature |

No violations. No complexity justification required.

## Project Structure

### Documentation (this feature)

```text
specs/001-python-project-setup/
├── plan.md              ← this file
├── research.md          ← build backend, toolchain decisions
├── data-model.md        ← filesystem entities and pyproject.toml schema
├── quickstart.md        ← developer onboarding guide
└── tasks.md             ← Phase 2 output (/speckit.tasks — not yet created)
```

### Source Code (repository root)

```text
credit-card-statement-extractor/
├── pyproject.toml
├── src/
│   └── credit_card_statement_extractor/
│       └── __init__.py
└── tests/
    └── __init__.py
```

**Structure Decision**: Single-project src-layout. The application package is `credit_card_statement_extractor` (matching the repository name, snake_case). `src/` contains exactly one package. `tests/` is a sibling to `src/`, not nested inside it.

## Implementation Notes

1. `pyproject.toml` must be created at the repo root with the schema documented in `data-model.md`.
2. `src/credit_card_statement_extractor/__init__.py` is a minimal file (empty or version string only).
3. `tests/__init__.py` is empty — its presence makes the directory a package, which avoids import collisions when test files share names across subdirectories.
4. No `requirements.txt`, `setup.py`, `setup.cfg`, or other legacy files.
5. `pytest` and `ruff` are declared as development dependencies under `[project.optional-dependencies]` or a `[dependency-groups]` dev group — not as runtime dependencies.
