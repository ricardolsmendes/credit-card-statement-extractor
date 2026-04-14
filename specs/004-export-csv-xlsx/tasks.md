# Tasks: Export Transactions to CSV and XLSX

**Input**: Design documents from `/specs/004-export-csv-xlsx/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Tests**: Included — Constitution §II mandates TDD. Tests MUST be written and confirmed failing before implementation.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- TDD: every test task must be confirmed failing before its implementation task runs

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add `xlsxwriter` optional extra to `pyproject.toml` so it can be installed for XLSX tests.

- [ ] T001 Add `xlsx = ["xlsxwriter>=3.0"]` optional extra to `pyproject.toml` under `[project.optional-dependencies]`; run `uv sync --all-extras` to install it

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No new fixtures needed — existing `en_statement.pdf`, `ptbr_statement.pdf`, and `ptbr_long_date_beneficiary_statement.pdf` are reused by all export tests. The only foundation needed is the `Exporter` skeleton (import-safe, raises `NotImplementedError`) so test files can import it without failing on import.

- [ ] T002 Create `src/credit_card_statement_extractor/transaction_extractor/_exporter.py` with an empty `Exporter` class stub (class body: `pass`) so test imports resolve

**Checkpoint**: `from credit_card_statement_extractor.transaction_extractor._exporter import Exporter` succeeds.

---

## Phase 3: User Story 1 — Export Transactions to CSV (Priority: P1) 🎯 MVP

**Goal**: `python -m credit_card_statement_extractor.transaction_extractor en_statement.pdf --output-format csv` writes `en_statement-transactions.csv` in the same directory as the PDF with correct headers and data rows.

**Independent Test**: Run `python -m credit_card_statement_extractor.transaction_extractor tests/fixtures/statements/en_statement.pdf --output-format csv` and confirm that `tests/fixtures/statements/en_statement-transactions.csv` is created with the expected content.

### Tests for User Story 1

> **NOTE: Write tests FIRST — confirm they FAIL before proceeding to implementation.**

- [ ] T003 [US1] Write unit tests in `tests/unit/transaction_extractor/test_exporter.py` — CSV scenarios: (a) `Exporter.export()` with 4 known transactions and `LOCALE_EN`, `fmt="csv"`, a `tmp_path` output path produces a file whose first line contains `Date,Description,Amount`; (b) the CSV has exactly 5 lines (1 header + 4 data rows); (c) date values are formatted as `YYYY-MM-DD` (ISO); (d) amount values are plain dot-decimal strings (e.g., `-4.50`, `+500.00` → `500.00`); (e) negative amounts are written without sign on positives; (f) `LOCALE_PT_BR` produces header `Data,Descrição,Valor` and date `01/03/2026`; (g) with `has_beneficiary=True`, header is `Date,Beneficiary,Description,Amount` (en) and `Data,Beneficiário,Descrição,Valor` (pt-BR); (h) file encoding is UTF-8 with BOM (read bytes and check for `b'\xef\xbb\xbf'` prefix)
- [ ] T004 [P] [US1] Write integration tests in `tests/integration/transaction_extractor/test_cli.py` — CSV export scenarios: (a) CLI with `en_statement.pdf --output-format csv` exits 0 and prints `Exported 4 transactions to` in stdout; (b) the output file `en_statement-transactions.csv` is created next to the fixture PDF; (c) the CSV contains `Date,Description,Amount` header; (d) the CSV contains `Coffee Shop` in a data row; (e) stdout does NOT contain the fixed-width table (no `----------` separator line); (f) CLI with `ptbr_statement.pdf --output-format csv --lang pt-BR` produces a file with `Data,Descrição,Valor` header; (g) CLI with `ptbr_long_date_beneficiary_statement.pdf --output-format csv --lang pt-BR` produces a file with `Beneficiário` in the header; (h) write-permission-denied: if the fixture path's parent is not writable, stderr contains "Cannot write" and exit is 1

### Implementation for User Story 1

- [ ] T005 [US1] Implement CSV writing in `src/credit_card_statement_extractor/transaction_extractor/_exporter.py` — replace stub: implement `Exporter` class with `export(self, transactions, locale, path, fmt, has_beneficiary=False)` method; implement `_write_csv(transactions, locale, path, has_beneficiary)` private method: open `path` with `encoding="utf-8-sig"`, `newline=""`, write header row using locale column labels, write one row per transaction with date formatted via `locale.date_format`, amount as plain dot-decimal string (no currency symbol, no thousands sep), beneficiary column inserted after date if `has_beneficiary=True`; dispatch from `export()` to `_write_csv()` when `fmt == "csv"` — T003 tests must pass
- [ ] T006 [US1] Update `src/credit_card_statement_extractor/transaction_extractor/__main__.py` — (1) add `--output-format` argument to `_build_arg_parser()` with `choices=["csv", "xlsx"]`, `default=None`; (2) after transactions are parsed, if `args.output_format` is set: derive `output_path = Path(args.file_path).resolve().parent / (Path(args.file_path).stem + f"-transactions.{args.output_format}")`; call `Exporter().export(transactions, locale, output_path, args.output_format, has_beneficiary=has_beneficiary)`; print `f"Exported {len(transactions)} transactions to {output_path.name}"` to stdout; wrap in `try/except (OSError, RuntimeError) as e` → `print(f"Error: {e}", file=sys.stderr); sys.exit(1)`; (3) if `args.output_format` is None, keep the existing `Formatter.render()` path unchanged — T004 tests must pass
- [ ] T007 [US1] Update `src/credit_card_statement_extractor/transaction_extractor/__init__.py` — add `Exporter` to the public exports list

**Checkpoint**: US1 done — `en_statement.pdf --output-format csv` produces a correct CSV file next to the PDF.

---

## Phase 4: User Story 2 — Export Transactions to XLSX (Priority: P2)

**Goal**: `python -m credit_card_statement_extractor.transaction_extractor en_statement.pdf --output-format xlsx` writes `en_statement-transactions.xlsx` with native date and numeric types.

**Independent Test**: Run `python -m credit_card_statement_extractor.transaction_extractor tests/fixtures/statements/en_statement.pdf --output-format xlsx` and confirm that `en_statement-transactions.xlsx` is created and can be opened, with date column containing date serials and amount column containing numbers.

### Tests for User Story 2

> **NOTE: Write tests FIRST — confirm they FAIL before proceeding to implementation.**

- [ ] T008 [US2] Extend unit tests in `tests/unit/transaction_extractor/test_exporter.py` — XLSX scenarios: (a) `Exporter.export()` with `fmt="xlsx"` and `tmp_path` creates a file that is a valid ZIP archive (XLSX files are ZIP — check `zipfile.is_zipfile(path)` returns True); (b) opening the workbook with `openpyxl` (or `xlsxwriter` — use `openpyxl` for reading back in tests if available, otherwise check file exists and size > 0); (c) the sheet named `Transactions` exists; (d) row 1 headers match locale column labels; (e) data rows exist for each transaction; (f) with `has_beneficiary=True`, beneficiary column is present in header; (g) if `xlsxwriter` is not installed, calling `export(..., fmt="xlsx")` raises `RuntimeError` containing "xlsxwriter" — test this by monkeypatching the import
- [ ] T009 [P] [US2] Extend integration tests in `tests/integration/transaction_extractor/test_cli.py` — XLSX export scenarios: (a) CLI with `en_statement.pdf --output-format xlsx` exits 0 and prints `Exported 4 transactions to` with `.xlsx` filename in stdout; (b) `en_statement-transactions.xlsx` is created next to the PDF and is a valid ZIP file; (c) stdout does NOT contain the fixed-width table; (d) CLI with `ptbr_statement.pdf --output-format xlsx --lang pt-BR` exits 0; (e) `--output-format xlsx` when xlsxwriter is not installed: stderr contains "xlsxwriter" and "pip install" and exit is 1 (test by temporarily removing/mocking the module — use `unittest.mock.patch.dict(sys.modules, {"xlsxwriter": None})` in subprocess or skip if difficult to mock in subprocess context — note this scenario and test it only in unit tests if subprocess mocking is impractical)

### Implementation for User Story 2

- [ ] T010 [US2] Implement XLSX writing in `src/credit_card_statement_extractor/transaction_extractor/_exporter.py` — add `_write_xlsx(transactions, locale, path, has_beneficiary)` private method: inside the method, `import xlsxwriter` (catches `ImportError` and raises `RuntimeError("XLSX export requires xlsxwriter. Install it with: pip install xlsxwriter")`); create a `Workbook` at `str(path)` with `{'remove_timezone': True}`; add worksheet named `Transactions`; write header row (bold format) using locale column labels; write one data row per transaction with `datetime.date` for date column (date format), `float(amount)` for amount column (numeric format `#,##0.00`), and `str` for description/beneficiary; close workbook; dispatch from `export()` when `fmt == "xlsx"` — T008 tests must pass

**Checkpoint**: US1 + US2 both functional. Both `--output-format csv` and `--output-format xlsx` produce correct output files.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T011 [P] Run `uv run pytest` — confirm all unit and integration tests pass with zero failures; confirm integration tests complete in under 5 seconds total (SC-001)
- [ ] T012 [P] Run `uv run ruff check .` and `uv run ruff format .` — confirm zero linting or formatting violations
- [ ] T013 Validate `quickstart.md` scenarios: run each example command from `specs/004-export-csv-xlsx/quickstart.md` and confirm output matches documented expected output (stdout confirmation messages and generated file content)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately ✅
- **Foundational (Phase 2)**: Depends on Phase 1 (xlsxwriter must be installed before tests) ✅
- **US1 (Phase 3)**: Depends on Phase 2 (stub `_exporter.py` must exist) ✅
- **US2 (Phase 4)**: Depends on Phase 3 (CSV path in `__main__.py` must exist; XLSX dispatch added to same `export()` method) ✅
- **Polish (Phase 5)**: Depends on Phases 3–4 ✅

### Within Each Phase

- Test tasks written and confirmed **FAILING** before their implementation counterpart
- T003 (unit tests) and T004 (integration tests) can be written in parallel — different files
- T008 (unit tests) and T009 (integration tests) can be written in parallel — different files
- T005 must complete before T006 (`__main__.py` calls `Exporter` which must exist)
- T010 extends `_exporter.py` from T005 — sequential within the same file

### Parallel Opportunities

- T003 and T004 are parallel (test_exporter.py vs test_cli.py — different files)
- T008 and T009 are parallel (same reason)
- T011 and T012 are parallel (independent validation steps)

---

## Parallel Example: User Story 1

```bash
# Write tests simultaneously (after T002 stub exists):
Task T003: test_exporter.py  (unit — Exporter CSV scenarios)
Task T004: test_cli.py       (integration — --output-format csv scenarios)

# Implement after tests are confirmed failing:
Task T005: _exporter.py      (CSV write logic)
Task T006: __main__.py       (--output-format arg + dispatch)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: add `xlsxwriter` extra, sync deps
2. Complete Phase 2: create `_exporter.py` stub
3. Complete Phase 3: CSV export end-to-end
4. **STOP and VALIDATE**: `en_statement.pdf --output-format csv` produces correct CSV
5. Continue to US2 (XLSX)

### Incremental Delivery

1. Setup + Foundational → dependency + stub ready
2. US1 complete → CSV export MVP; zero new required deps for users
3. US2 complete → XLSX export available for users with `xlsxwriter` installed

---

## Notes

- [P] tasks touch different files with no blocking dependencies
- [Story] label maps each task to a specific user story
- TDD is mandatory (Constitution §II): red → green → refactor
- `Exporter.export()` is the single public entry point; all format logic is in private methods
- `__main__.py` change must NOT break any of the 162 existing passing tests — the `--output-format` flag is additive
- Integration tests should clean up generated files (`en_statement-transactions.csv` etc.) after each test run using `tmp_path` or explicit cleanup to avoid polluting the fixtures directory
- XLSX unit tests use `zipfile.is_zipfile()` for structural validation (no need to install `openpyxl` as a test dep — XLSX is a ZIP)
- The `--output-format xlsx` missing-library error should be tested in unit tests (mock `sys.modules`); integration test for this scenario is optional/skipped if subprocess mocking is impractical
