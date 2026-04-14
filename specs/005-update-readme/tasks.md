# Tasks: Update README with Capabilities and Developer Guide

**Input**: Design documents from `/specs/005-update-readme/`
**Prerequisites**: plan.md ✓, spec.md ✓

**Tests**: Not applicable — this feature is pure documentation. Acceptance is manual review against FR-001–FR-010.

**Organization**: Tasks grouped by user story. Each story produces an independently reviewable increment of `README.md`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Read the current README and gather reference content from existing docs before writing.

- [X] T001 Read `README.md` (current one-liner) and `specs/004-export-csv-xlsx/quickstart.md` to extract all CLI invocations and expected output examples to be used in the new README

**Checkpoint**: Content gathered — CLI examples, output samples, and current description available for reference.

---

## Phase 2: User Story 1 — User-Facing README Content (Priority: P1) 🎯 MVP

**Goal**: A new user can install the tool and run their first CLI command in under 5 minutes by reading `README.md` alone.

**Independent Test**: Read the new README top-to-bottom without any other context and verify:
- (a) Purpose is clear in one paragraph
- (b) Installation steps are complete and runnable
- (c) At least one `--output-format csv` example is shown with expected output
- (d) All CLI flags are documented

### Implementation for User Story 1

- [X] T002 [US1] Write the Overview section in `README.md` — expand the existing one-sentence description into 2–3 sentences covering: what the tool does (extract credit card transactions from PDF statements), supported output formats (table/CSV/XLSX), and who it is for (developers/analysts); preserve the existing mention of Claude Code and GitHub Speckit as the project's learning context (FR-001, FR-010)
- [X] T003 [US1] Write the Installation section in `README.md` — include: (1) clone the repo; (2) `uv sync --all-extras` as primary install; (3) optional note for XLSX: `uv sync --extra xlsx`; (4) brief `pip install -e .` fallback for users without `uv` (FR-002)
- [X] T004 [US1] Write the Usage section in `README.md` with three subsections: (a) **Basic table output** — `python -m credit_card_statement_extractor.transaction_extractor statement.pdf` with sample tabular output block (header + separator + 4 rows); (b) **Export to CSV** — `--output-format csv` invocation + sample `statement-transactions.csv` content block (5 lines: header + 4 rows); (c) **Export to XLSX** — `--output-format xlsx` invocation + one-line note that a native Excel file is created; use output examples from `specs/004-export-csv-xlsx/quickstart.md` (FR-003, FR-004)
- [X] T005 [US1] Write the CLI Reference section in `README.md` — a Markdown table with columns: Argument, Type, Default, Description; rows for `file_path` (positional, required), `--lang` (en | pt-BR, default en), `--output-format` (csv | xlsx, default omitted → prints table); note that omitting `--output-format` prints a formatted table to stdout (FR-005)

**Checkpoint**: US1 done — a new user can install and run the tool from README alone.

---

## Phase 3: User Story 2 — Developer's Guide (Priority: P2)

**Goal**: A contributor can read the Developer's Guide section and understand the development tools and workflow without consulting any other document.

**Independent Test**: Read only the Developer's Guide section and verify:
- (a) Claude Code is named and its role described
- (b) GitHub Speckit is named and its role described
- (c) Commands for running tests and linting are present

### Implementation for User Story 2

- [X] T006 [US2] Write the Developer's Guide section in `README.md` — include three subsections: (a) **Development Tools** — bullet for Claude Code (link to `https://claude.ai/code`): "AI-powered CLI used for all implementation tasks — writes, edits, and runs code from natural language instructions"; bullet for GitHub Speckit (link to `https://github.com/github/spec-kit`): "Specification-driven workflow tool — used to write specs, generate implementation plans, and drive TDD task breakdowns before any code is written"; (b) **Development Commands** — code block with `uv sync --all-extras`, `uv run pytest`, `uv run ruff check .`, `uv run ruff format .`; (c) brief note that all features follow the Speckit workflow: specify → clarify → plan → tasks → implement (FR-006, FR-007, FR-008)

**Checkpoint**: US1 + US2 done. README covers user and contributor needs.

---

## Phase 4: Polish & Validation

- [X] T007 Review the completed `README.md` against each Functional Requirement (FR-001–FR-010) — for each FR, confirm it is satisfied by a specific section; flag any gap and fix before marking complete
- [X] T008 [P] Verify all Markdown syntax in `README.md` — check: (a) no broken section headings; (b) code blocks all have language tags; (c) links to Claude Code and GitHub Speckit use correct URLs; (d) CLI reference table renders correctly; (e) no raw HTML

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately ✅
- **US1 (Phase 2)**: Depends on T001 (need gathered content) ✅
- **US2 (Phase 3)**: Independent of US1 — can be written in any order, but logically follows US1 since the Developer's Guide section appears after Usage ✅
- **Polish (Phase 4)**: Depends on US1 + US2 ✅

### Within Each Phase

- T002, T003, T004, T005 are sequential — all write to `README.md` in order
- T006 continues writing `README.md` after T005
- T007 and T008 are parallel validation steps

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: gather content
2. Complete Phase 2 (T002–T005): write user-facing sections
3. **STOP and VALIDATE**: README section headers and content are coherent; can be installed and used from README alone
4. Continue to US2 (Developer's Guide)

### Incremental Delivery

1. T001 → content gathered
2. T002–T005 → user-facing README complete (MVP)
3. T006 → Developer's Guide added
4. T007–T008 → validation complete

---

## Notes

- All tasks write to a single file `README.md` — tasks must run sequentially within each phase
- No automated tests; validation is manual review against FR checklist in T007
- Output examples should be copy-pasted from `specs/004-export-csv-xlsx/quickstart.md` to ensure accuracy
- The existing README content (one paragraph) must appear in or inform the Overview section — do not discard it
