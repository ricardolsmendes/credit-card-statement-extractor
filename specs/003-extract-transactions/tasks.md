# Tasks: Transaction Extractor

**Input**: Design documents from `/specs/003-extract-transactions/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Tests**: Included — Constitution §II mandates TDD. Tests MUST be written and confirmed failing before implementation.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- TDD: every test task must be confirmed failing before its implementation task runs

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create package skeleton and test directory structure.

- [ ] T001 Create `src/credit_card_statement_extractor/transaction_extractor/` with empty `__init__.py`
- [ ] T002 [P] Create `tests/unit/transaction_extractor/__init__.py` and `tests/integration/transaction_extractor/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Statement fixture PDFs required by all user story tests.

**⚠️ CRITICAL**: No user story tests can run until these fixtures exist.

- [ ] T003 Write `tests/fixtures/statements/create_fixtures.py` — pure-Python PDF generator producing `en_statement.pdf` (English headers: Date / Description / Amount; 4 transactions with known dates, descriptions, amounts including one negative) and `ptbr_statement.pdf` (pt-BR headers: Data / Descrição / Valor; same 4 transactions in pt-BR date and amount format)
- [ ] T004 Run `tests/fixtures/statements/create_fixtures.py` to generate `tests/fixtures/statements/en_statement.pdf` and `tests/fixtures/statements/ptbr_statement.pdf`

**Checkpoint**: Fixture PDFs ready — user story phases can now begin.

---

## Phase 3: User Story 1 — Extract and Display Transactions (Priority: P1) 🎯 MVP

**Goal**: Given a valid PDF statement, extract all transactions and print a fixed-width English table to stdout.

**Independent Test**: Run `python -m credit_card_statement_extractor.transaction_extractor tests/fixtures/statements/en_statement.pdf` and confirm a table with 4 known transactions appears on stdout, in source order, with correct dates, descriptions, and amounts.

### Tests for User Story 1

> **NOTE: Write tests FIRST — confirm they FAIL before proceeding to implementation.**

- [ ] T005 Write `tests/unit/transaction_extractor/test_models.py` — Transaction frozen dataclass: valid construction with date/description/amount, empty description raises ValueError, amount stored as Decimal, mutation raises FrozenInstanceError, negative amount accepted
- [ ] T006 Write `tests/unit/transaction_extractor/test_parser.py` — DefaultParser US1 scenarios: header detection using English headers ("Date", "Description", "Amount"), 4-row parse returns 4 Transactions in source order, dates parsed correctly, amounts parsed as Decimal, no-header PDF raises ValueError, NullParser satisfies TransactionParser protocol, non-parser does not satisfy protocol
- [ ] T007 [P] Write `tests/unit/transaction_extractor/test_formatter.py` — Formatter US1 scenarios (English locale): header row contains "Date" / "Description" / "Amount", separator line length matches header, each transaction row contains formatted date (YYYY-MM-DD), description, and amount, negative amounts prefixed with `-`, positive amounts prefixed with `+`, column widths accommodate longest value

### Implementation for User Story 1

- [ ] T008 Implement `src/credit_card_statement_extractor/transaction_extractor/_models.py` — `Transaction` frozen dataclass with `date: datetime.date`, `description: str` (raises ValueError if empty after strip), `amount: decimal.Decimal` — T005 tests must pass
- [ ] T009 [P] Implement `src/credit_card_statement_extractor/transaction_extractor/_protocol.py` — `@runtime_checkable TransactionParser` Protocol with `parse(pages: list[PageResult]) -> list[Transaction]`; can be written in parallel with T008 (different file)
- [ ] T010 Implement `src/credit_card_statement_extractor/transaction_extractor/_parser.py` — `DefaultParser` with: header detection scanning all lines for recognised date / description / amount labels (English + pt-BR variants from clarifications), transaction regex `^(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\s+(.+?)\s{2,}([+\-]?\d[\d.,]*)$`, multi-format date parsing (`%d/%m/%Y` → `%Y-%m-%d` → `%m/%d/%Y` → `%d/%m/%y`), amount normalisation heuristic (last separator before final 1–2 digits determines decimal), raises ValueError if no header found, returns transactions in source order — T006 tests must pass
- [ ] T011 Add timing smoke test to `tests/unit/transaction_extractor/test_parser.py` — parsing `en_statement.pdf` via DefaultParser completes in < 2 s (Constitution §V; stricter than SC-001's 10 s target)
- [ ] T012 Implement `src/credit_card_statement_extractor/transaction_extractor/_formatter.py` — `Formatter` class: `render(transactions: list[Transaction], locale: LocaleConfig) -> str` produces fixed-width table with header row, separator line, one row per transaction; dynamic column widths (max content length, min: date=10, description=20, amount=12); date column left-aligned, description left-aligned, amount right-aligned; columns separated by two spaces — T007 tests must pass
- [ ] T013 Write US1 integration tests in `tests/integration/transaction_extractor/test_cli.py` — exit 0 on valid en_statement.pdf, "Date" / "Description" / "Amount" headers in stdout, 4 transaction rows in stdout, transactions in source order, negative amount starts with `-`, stdout empty on error exits
- [ ] T014 Implement `src/credit_card_statement_extractor/transaction_extractor/__main__.py` — `main()`: requires one positional argument (file path); uses `PdfplumberReader` → `DefaultParser` → `Formatter` with English locale; catches `FileNotFoundError` → stderr + exit 1, `ValueError` from PDF parse → stderr + exit 2, `ValueError` from no transactions → stderr + exit 2, unexpected exceptions → stderr + exit 3; no `--lang` flag yet (added in US2) — T013 tests must pass

**Checkpoint**: US1 fully functional — `python -m credit_card_statement_extractor.transaction_extractor statement.pdf` prints a correct English table.

---

## Phase 4: User Story 2 — View Output in a Selected Language (Priority: P2)

**Goal**: Add `--lang en` / `--lang pt-BR` argument; all output labels, date format, and amount format switch accordingly.

**Independent Test**: Run with `--lang pt-BR` on `ptbr_statement.pdf` and confirm: column headers are "Data" / "Descrição" / "Valor", dates are DD/MM/YYYY, amounts have `R$` prefix with comma-decimal, minus-sign negatives.

### Tests for User Story 2

> **NOTE: Write tests FIRST — confirm they FAIL before proceeding to implementation.**

- [ ] T015 Write `tests/unit/transaction_extractor/test_locale.py` — LOCALE_EN and LOCALE_PT_BR constants: correct date formats, decimal/thousands separators, currency prefixes, column label strings; amount formatting for positive and negative Decimals; date formatting for a known date in both locales
- [ ] T016 [P] Extend `tests/unit/transaction_extractor/test_formatter.py` — add pt-BR locale test cases: header contains "Data" / "Descrição" / "Valor", dates use DD/MM/YYYY, amounts use R$ prefix with comma decimal and period thousands, negative amounts use `-R$ `

### Implementation for User Story 2

- [ ] T017 Implement `src/credit_card_statement_extractor/transaction_extractor/_locale.py` — `LocaleConfig` frozen dataclass (`code`, `date_format`, `decimal_separator`, `thousands_separator`, `currency_prefix`, `col_date`, `col_description`, `col_amount`) and two module-level constants: `LOCALE_EN` and `LOCALE_PT_BR` — T015 tests must pass
- [ ] T018 Update `src/credit_card_statement_extractor/transaction_extractor/_formatter.py` — `Formatter.render()` accepts `locale: LocaleConfig`; formats dates with `locale.date_format`, formats amounts with locale separators and currency prefix, uses locale column labels — T016 tests must pass
- [ ] T019 Add US2 integration tests to `tests/integration/transaction_extractor/test_cli.py` — `--lang pt-BR` on ptbr_statement.pdf: exit 0, "Data"/"Descrição"/"Valor" in stdout, dates in DD/MM/YYYY, amounts with `R$` and comma-decimal; `--lang en` explicit: behaves identically to default; no `--lang`: defaults to English (FR-007)
- [ ] T020 Update `src/credit_card_statement_extractor/transaction_extractor/__main__.py` — add `--lang` argument (choices: `en`, `pt-BR`; default: `en`); resolve `LocaleConfig` from argument and pass to `Formatter` — T019 tests must pass
- [ ] T021 Implement `src/credit_card_statement_extractor/transaction_extractor/__init__.py` — export public API: `Transaction`, `TransactionParser`, `DefaultParser`, `LocaleConfig`, `LOCALE_EN`, `LOCALE_PT_BR`, `Formatter`

**Checkpoint**: US1 + US2 both functional. Language flag controls all locale-specific output.

---

## Phase 5: User Story 3 — Graceful Handling of Unrecognised or Empty Statements (Priority: P3)

**Goal**: All error paths (no arg, bad file, non-PDF, no transactions, partial parse) produce clear stderr messages and correct exit codes; stdout is clean on failure.

**Independent Test**: Run with a PDF containing no transaction header — confirm "No transactions found" on stderr, exit 2, empty stdout.

### Tests for User Story 3

> **NOTE: Write tests FIRST — confirm they FAIL before proceeding to implementation.**

- [ ] T022 Add US3 integration tests to `tests/integration/transaction_extractor/test_cli.py` — no argument → exit 1 + usage on stderr; missing file → exit 1 + "not found" on stderr; non-PDF → exit 2 + "parse" on stderr; PDF with no transaction header → exit 2 + "No transactions found" on stderr; PDF with mixed parseable/unparseable rows → exit 0 + warning on stderr + partial table on stdout; stdout empty for all non-zero exits
- [ ] T023 Add US3 unit tests to `tests/unit/transaction_extractor/test_parser.py` — partial parse: lines not matching transaction regex are skipped and counted; parse returns only valid transactions and raises no exception; total-line PDF (only header + totals row, no transaction rows) raises ValueError

### Implementation for User Story 3

- [ ] T024 Update `src/credit_card_statement_extractor/transaction_extractor/__main__.py` — complete all error paths: no argument → usage + exit 1; `FileNotFoundError` → "File not found: <path>" + exit 1; PDF `ValueError` → "Could not parse as PDF: <path>" + exit 2; empty transaction list → "No transactions found in <path>" + exit 2; partial parse (DefaultParser returns skip count) → "Warning: N line(s) could not be parsed and were skipped." to stderr, continue with exit 0; unhandled exception → "An unexpected error occurred. Please report this issue." + exit 3 — T022 tests must pass
- [ ] T025 Update `src/credit_card_statement_extractor/transaction_extractor/_parser.py` — expose skip count from `parse()`: return `(list[Transaction], int)` where int = number of skipped lines; update callers accordingly — T023 tests must pass

**Checkpoint**: All three user stories functional. Full error handling in place per FR-010, FR-011, FR-012.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T026 [P] Add timing smoke test to `tests/integration/transaction_extractor/test_cli.py` — full CLI invocation on `en_statement.pdf` completes in < 2 s end-to-end (SC-001 / Constitution §V)
- [ ] T027 Run `uv run pytest` — confirm all unit and integration tests pass with zero failures
- [ ] T028 Run `uv run ruff check .` and `uv run ruff format .` — confirm zero linting or formatting violations
- [ ] T029 Validate `quickstart.md` scenarios manually: English extraction, pt-BR extraction, and all error cases produce output matching the documented examples

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1
- **US1 (Phase 3)**: Depends on Phase 2 (fixtures must exist before integration tests)
- **US2 (Phase 4)**: Depends on Phase 3 (locale extends the formatter built in US1)
- **US3 (Phase 5)**: Depends on Phase 3 (error paths extend `__main__.py` from US1)
- **Polish (Phase 6)**: Depends on Phases 3–5 complete

### Within Each Phase

- Test tasks written and confirmed **FAILING** before their implementation counterpart
- Models before services (`_models.py` before `_parser.py`)
- Protocol before concrete implementation (`_protocol.py` before `_parser.py`)
- Core components before CLI (`_parser.py`, `_formatter.py` before `__main__.py`)

### Parallel Opportunities

- T001 and T002 are parallel (different directories)
- T007 and T006 can be written simultaneously after T005+T008 (different test files)
- T009 and T008 parallel within US1 (different source files)
- T015 and T016 parallel within US2 (test_locale.py vs. test_formatter.py extension)
- T026, T027, T028 parallel in Polish phase (independent validation steps)

---

## Parallel Example: User Story 1

```bash
# Write tests (both can be written simultaneously after T005):
Task T006: test_models.py
Task T007: test_formatter.py (skeleton)

# Implement core components (after respective tests are confirmed failing):
Task T009: _protocol.py   # parallel with T008
Task T010: _parser.py     # depends on T008 + T009
Task T012: _formatter.py  # depends on T007
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (fixtures)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: `python -m credit_card_statement_extractor.transaction_extractor en_statement.pdf` prints correct table
5. Continue to US2 / US3 as capacity allows

### Incremental Delivery

1. Setup + Foundational → fixtures ready
2. US1 complete → English extraction MVP
3. US2 complete → locale-aware output
4. US3 complete → production-grade error handling

---

## Notes

- [P] tasks touch different files with no blocking dependencies
- [Story] label maps each task to a specific user story
- TDD is mandatory (Constitution §II): red → green → refactor
- `DefaultParser.parse()` return type changes in T025 (adds skip count) — update all call sites
- Statement fixture PDFs in `tests/fixtures/statements/` are the ground truth for parser correctness tests
- `_parser.py` header detection must recognise all variants documented in spec.md Clarifications
