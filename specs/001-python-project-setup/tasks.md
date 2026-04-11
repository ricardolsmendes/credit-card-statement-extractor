# Tasks: Python Project Setup

**Input**: Design documents from `specs/001-python-project-setup/`  
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, quickstart.md ✓

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the project skeleton that all user stories depend on

- [x] T001 Create `src/credit_card_statement_extractor/` directory with empty `__init__.py`
- [x] T002 Create `tests/` directory with empty `__init__.py`
- [x] T003 Create `pyproject.toml` at the repository root with the schema from `specs/001-python-project-setup/data-model.md`

**Checkpoint**: Repository root contains `src/`, `tests/`, and `pyproject.toml`. No other config files present.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Validate the scaffold is coherent before any application code is added

**⚠️ CRITICAL**: Phases 3–5 depend on this phase completing successfully

- [x] T004 Verify `pyproject.toml` is valid by running `uv sync --all-extras` and confirming no errors
- [x] T005 Verify pytest discovers the `tests/` directory by running `uv run pytest --collect-only` and confirming zero errors (empty collection is acceptable at this stage)
- [x] T006 Verify the application package is importable by running `uv run python -c "import credit_card_statement_extractor"` from the project root

**Checkpoint**: Foundation valid — all three verification commands exit 0.

---

## Phase 3: User Story 1 - Developer Runs Application Code (Priority: P1) 🎯 MVP

**Goal**: A developer can locate and place application source code in `src/credit_card_statement_extractor/` and have it recognised as part of the project.

**Independent Test**: Navigate to `src/credit_card_statement_extractor/`, add a trivial module (`version.py`), and confirm it is importable from the project root without modifying any configuration.

### Implementation for User Story 1

- [x] T007 [US1] Add `version = "0.1.0"` to `src/credit_card_statement_extractor/__init__.py` so the package has a meaningful importable attribute
- [x] T008 [US1] Confirm `uv run python -c "from credit_card_statement_extractor import version; print(version)"` prints `0.1.0` — verifies the src-layout is correctly wired in `pyproject.toml`

**Checkpoint**: User Story 1 complete — application package is discoverable and importable from `src/` without any path manipulation.

---

## Phase 4: User Story 2 - Developer Runs Tests (Priority: P2)

**Goal**: A developer can place test files in `tests/` and run them with a single command from the project root.

**Independent Test**: Place a trivial passing test in `tests/test_smoke.py` and confirm `pytest` discovers and runs it without any additional configuration.

### Implementation for User Story 2

- [x] T009 [US2] Create `tests/test_smoke.py` containing one trivial passing test (`def test_import(): from credit_card_statement_extractor import version; assert version`) to prove the full test pipeline works
- [x] T010 [US2] Run `uv run pytest` from the project root and confirm T009's test is discovered, executed, and passes — verifies `testpaths` and `pythonpath` in `pyproject.toml` are correctly configured
- [x] T011 [US2] Run `uv run pytest --collect-only` and confirm no warnings about import paths or missing `conftest.py` — verifies clean discovery with zero configuration overhead for contributors

**Checkpoint**: User Story 2 complete — tests in `tests/` are auto-discovered and pass with a single `uv run pytest` invocation.

---

## Phase 5: User Story 3 - Developer Inspects or Updates Project Configuration (Priority: P3)

**Goal**: All project configuration lives in `pyproject.toml`; no other config files are needed or present.

**Independent Test**: Open `pyproject.toml` and confirm it contains all mandatory sections (build-system, project metadata, pytest config, ruff config). Confirm no `setup.py`, `setup.cfg`, `tox.ini`, `.flake8`, or `requirements.txt` exist at the root.

### Implementation for User Story 3

- [x] T012 [P] [US3] Add `[tool.ruff]` section to `pyproject.toml` with `line-length`, `target-version`, `[tool.ruff.lint] select`, and `[tool.ruff.format] quote-style` per `data-model.md`
- [x] T013 [P] [US3] Add `[project.optional-dependencies]` dev group to `pyproject.toml` declaring `pytest` and `ruff` as development dependencies (not runtime)
- [x] T014 [US3] Run `uv run ruff check .` from the project root and confirm it exits 0 with no violations — verifies Ruff is correctly configured via `pyproject.toml`
- [x] T015 [US3] Verify no legacy configuration files exist at the repository root: confirm absence of `setup.py`, `setup.cfg`, `tox.ini`, `.flake8`, `requirements.txt`, and `Pipfile`

**Checkpoint**: User Story 3 complete — `pyproject.toml` is the single source of all project configuration; all tooling reads from it without additional files.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation across all user stories

- [x] T016 [P] Run `ruff format --check .` to confirm formatting baseline is clean
- [x] T017 [P] Run `uv run pytest -v` to confirm all tests pass and output is clear
- [x] T018 Validate `quickstart.md` by executing each command in `specs/001-python-project-setup/quickstart.md` in sequence and confirming all exit 0
- [x] T019 Confirm the project root contains only: `pyproject.toml`, `src/`, `tests/`, `specs/`, `.specify/`, `CLAUDE.md`, `.git/`, and `README.md` (if present) — no configuration file sprawl

---

---

## Phase 7: Clarification — Switch to uv (FR-009, FR-010)

**Purpose**: Apply spec clarifications — replace pip with uv as the sole dependency manager and make virtual environment usage explicit

- [x] T020 Run `uv sync` from the project root to create `uv.lock` and a `.venv` managed by uv
- [x] T021 Verify `uv run pytest` executes the test suite successfully — confirms uv manages the venv and pytest is accessible without manual activation
- [x] T022 Verify `uv run ruff check .` exits 0 — confirms ruff is accessible via uv
- [x] T023 Update `specs/001-python-project-setup/quickstart.md` to replace `pip install -e .`, `pytest`, and `ruff` commands with `uv sync`, `uv run pytest`, and `uv run ruff check .`
- [x] T024 Update `CLAUDE.md` to reflect uv-based commands

**Checkpoint**: All developer workflow commands use `uv run`; `uv.lock` committed; no pip references in documentation.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — **blocks Phases 3–5**
- **User Stories (Phases 3–5)**: All depend on Phase 2 completion
  - US1, US2, US3 can proceed sequentially or in parallel once Phase 2 is done
- **Polish (Phase 6)**: Depends on all desired user story phases being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — no dependency on US2 or US3
- **US2 (P2)**: Can start after Phase 2 — depends on US1 being complete (imports the package)
- **US3 (P3)**: Can start after Phase 2 — independent of US1 and US2 (config only)

### Within Each User Story

- Verification tasks depend on the files they verify being created first
- T012 and T013 in US3 are independent of each other ([P])
- T016 and T017 in Phase 6 are independent of each other ([P])

---

## Parallel Example: Phase 1

```bash
# T001 and T002 can be created at the same time (different directories):
Task: "Create src/credit_card_statement_extractor/__init__.py"
Task: "Create tests/__init__.py"

# T003 depends on neither — can overlap:
Task: "Create pyproject.toml"
```

## Parallel Example: User Story 3

```bash
# T012 and T013 touch different sections of pyproject.toml — safe to plan in parallel:
Task: "Add [tool.ruff] section to pyproject.toml"
Task: "Add [project.optional-dependencies] dev group to pyproject.toml"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T003)
2. Complete Phase 2: Foundational (T004–T006)
3. Complete Phase 3: User Story 1 (T007–T008)
4. **STOP and VALIDATE**: Application code in `src/` is importable ✓

### Incremental Delivery

1. Phase 1 + Phase 2 → scaffold valid
2. Phase 3 (US1) → source layout works, package importable (MVP)
3. Phase 4 (US2) → test runner works, single-command test execution
4. Phase 5 (US3) → all config centralised in `pyproject.toml`
5. Phase 6 → cross-cutting validation

---

## Notes

- [P] tasks operate on different files or independent sections — safe to parallelise
- No TDD test tasks generated: this feature creates files/config, not business logic functions
- The smoke test in T009 is a *verification artefact*, not a production test — it may be removed or replaced once real tests exist
- Commit after each phase checkpoint
- Run `quickstart.md` commands as the final end-to-end validation (T018)
