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

- [X] T001 Create `src/credit_card_statement_extractor/transaction_extractor/` with empty `__init__.py`
- [X] T002 [P] Create `tests/unit/transaction_extractor/__init__.py` and `tests/integration/transaction_extractor/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Statement fixture PDFs required by all user story tests.

**⚠️ CRITICAL**: No user story tests can run until these fixtures exist.

- [X] T003 Write `tests/fixtures/statements/create_fixtures.py` — pure-Python PDF generator producing four fixtures: (1) `en_statement.pdf` (English headers: Date / Description / Amount; 4 transactions with known dates, descriptions, amounts including one negative; lines must have ≥2 spaces between description and amount to match the parser regex); (2) `ptbr_statement.pdf` (pt-BR headers: Data / Descrição / Valor; same 4 transactions in pt-BR date and amount format); (3) `no_transactions_statement.pdf` (valid PDF, account summary text but no transaction header row); (4) `partial_statement.pdf` (valid PDF, 2 parseable transaction lines + 2 malformed lines that lack a date or amount)
- [X] T004 Run `tests/fixtures/statements/create_fixtures.py` to generate all four fixtures: `en_statement.pdf`, `ptbr_statement.pdf`, `no_transactions_statement.pdf`, `partial_statement.pdf`

**Checkpoint**: Fixture PDFs ready — user story phases can now begin.

---

## Phase 3: User Story 1 — Extract and Display Transactions (Priority: P1) 🎯 MVP

**Goal**: Given a valid PDF statement, extract all transactions and print a fixed-width English table to stdout.

**Independent Test**: Run `python -m credit_card_statement_extractor.transaction_extractor tests/fixtures/statements/en_statement.pdf` and confirm a table with 4 known transactions appears on stdout, in source order, with correct dates, descriptions, and amounts.

### Tests for User Story 1

> **NOTE: Write tests FIRST — confirm they FAIL before proceeding to implementation.**

- [X] T005 Write `tests/unit/transaction_extractor/test_models.py` — Transaction frozen dataclass: valid construction with date/description/amount, empty description raises ValueError, amount stored as Decimal, mutation raises FrozenInstanceError, negative amount accepted
- [X] T006 Write `tests/unit/transaction_extractor/test_parser.py` — DefaultParser US1 scenarios: header detection using English headers ("Date", "Description", "Amount"), 4-row parse returns 4 Transactions in source order, dates parsed correctly, amounts parsed as Decimal, no-header PDF raises ValueError, NullParser satisfies TransactionParser protocol, non-parser does not satisfy protocol; multi-page spanning: given 2 PageResult objects where the header is on page 1 and transaction rows continue onto page 2, all transactions are returned (covers spec.md edge case)
- [X] T006b [P] Write `tests/unit/transaction_extractor/test_locale.py` for `LOCALE_EN` only — correct date format (`%Y-%m-%d`), empty currency prefix, column labels "Date"/"Description"/"Amount", amount formatting for a known positive and negative Decimal; `LOCALE_PT_BR` tests added in US2 (T015)
- [X] T006c Implement `src/credit_card_statement_extractor/transaction_extractor/_locale.py` — `LocaleConfig` frozen dataclass with fields: `code`, `date_format`, `decimal_separator`, `thousands_separator`, `currency_prefix`, `col_date`, `col_description`, `col_amount`; export `LOCALE_EN` constant; `LOCALE_PT_BR` added in T017 — T006b tests must pass
- [X] T007 [P] Write `tests/unit/transaction_extractor/test_formatter.py` — Formatter US1 scenarios (English locale using `LOCALE_EN` from `_locale.py`): header row contains "Date" / "Description" / "Amount", separator line length matches header, each transaction row contains formatted date (YYYY-MM-DD), description, and amount, negative amounts prefixed with `-`, positive amounts prefixed with `+`, column widths accommodate longest value; requires T006c complete

### Implementation for User Story 1

- [X] T008 Implement `src/credit_card_statement_extractor/transaction_extractor/_models.py` — `Transaction` frozen dataclass with `date: datetime.date`, `description: str` (raises ValueError if empty after strip), `amount: decimal.Decimal` — T005 tests must pass
- [X] T009 [P] Implement `src/credit_card_statement_extractor/transaction_extractor/_protocol.py` — `@runtime_checkable TransactionParser` Protocol with `parse(pages: list[PageResult]) -> list[Transaction]`; can be written in parallel with T008 (different file)
- [X] T010 Implement `src/credit_card_statement_extractor/transaction_extractor/_parser.py` — `DefaultParser` with: header detection scanning all lines for recognised date / description / amount labels (English + pt-BR variants from clarifications), transaction regex `^(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\s+(.+?)\s{2,}([+\-]?\d[\d.,]*)$`, multi-format date parsing (`%d/%m/%Y` → `%Y-%m-%d` → `%m/%d/%Y` → `%d/%m/%y`), amount normalisation heuristic (last separator before final 1–2 digits determines decimal), raises ValueError if no header found, returns transactions in source order — T006 tests must pass
- [X] T011 Add timing smoke test to `tests/unit/transaction_extractor/test_parser.py` — parsing `en_statement.pdf` via DefaultParser completes in < 2 s (Constitution §V; stricter than SC-001's 10 s target)
- [X] T012 Implement `src/credit_card_statement_extractor/transaction_extractor/_formatter.py` — `Formatter` class: `render(transactions: list[Transaction], locale: LocaleConfig) -> str` produces fixed-width table with header row, separator line, one row per transaction; dynamic column widths (max content length, min: date=10, description=20, amount=12); date column left-aligned, description left-aligned, amount right-aligned; columns separated by two spaces; imports `LocaleConfig` from `_locale.py` (available since T006c) — T007 tests must pass
- [X] T013 Write US1 integration tests in `tests/integration/transaction_extractor/test_cli.py` — exit 0 on valid en_statement.pdf, "Date" / "Description" / "Amount" headers in stdout, 4 transaction rows in stdout, transactions in source order, negative amount starts with `-`, stdout empty on error exits
- [X] T014 Implement `src/credit_card_statement_extractor/transaction_extractor/__main__.py` — `main()`: requires one positional argument (file path); uses `PdfplumberReader` → `DefaultParser` → `Formatter` with English locale; catches `FileNotFoundError` → stderr + exit 1, `ValueError` from PDF parse → stderr + exit 2, `ValueError` from no transactions → stderr + exit 2, unexpected exceptions → stderr + exit 3; no `--lang` flag yet (added in US2) — T013 tests must pass

**Checkpoint**: US1 fully functional — `python -m credit_card_statement_extractor.transaction_extractor statement.pdf` prints a correct English table.

---

## Phase 4: User Story 2 — View Output in a Selected Language (Priority: P2)

**Goal**: Add `--lang en` / `--lang pt-BR` argument; all output labels, date format, and amount format switch accordingly.

**Independent Test**: Run with `--lang pt-BR` on `ptbr_statement.pdf` and confirm: column headers are "Data" / "Descrição" / "Valor", dates are DD/MM/YYYY, amounts have `R$` prefix with comma-decimal, minus-sign negatives.

### Tests for User Story 2

> **NOTE: Write tests FIRST — confirm they FAIL before proceeding to implementation.**

- [X] T015 Extend `tests/unit/transaction_extractor/test_locale.py` — add `LOCALE_PT_BR` test cases: date format `%d/%m/%Y`, decimal separator `,`, thousands separator `.`, currency prefix `R$ `, column labels "Data"/"Descrição"/"Valor"; amount formatting for positive and negative Decimals in pt-BR convention; date formatting for a known date
- [X] T016 [P] Extend `tests/unit/transaction_extractor/test_formatter.py` — add pt-BR locale test cases: header contains "Data" / "Descrição" / "Valor", dates use DD/MM/YYYY, amounts use R$ prefix with comma decimal and period thousands, negative amounts use `-R$ `

### Implementation for User Story 2

- [X] T017 Update `src/credit_card_statement_extractor/transaction_extractor/_locale.py` — add `LOCALE_PT_BR` constant (`date_format="%d/%m/%Y"`, `decimal_separator=","`, `thousands_separator="."`, `currency_prefix="R$ "`, `col_date="Data"`, `col_description="Descrição"`, `col_amount="Valor"`) — T015 tests must pass
- [X] T018 Update `src/credit_card_statement_extractor/transaction_extractor/_formatter.py` — `Formatter.render()` accepts `locale: LocaleConfig`; formats dates with `locale.date_format`, formats amounts with locale separators and currency prefix, uses locale column labels — T016 tests must pass
- [X] T019 Add US2 integration tests to `tests/integration/transaction_extractor/test_cli.py` — `--lang pt-BR` on ptbr_statement.pdf: exit 0, "Data"/"Descrição"/"Valor" in stdout, dates in DD/MM/YYYY, amounts with `R$` and comma-decimal; `--lang en` explicit: behaves identically to default; no `--lang`: defaults to English (FR-007)
- [X] T020 Update `src/credit_card_statement_extractor/transaction_extractor/__main__.py` — add `--lang` argument (choices: `en`, `pt-BR`; default: `en`); resolve `LocaleConfig` from argument and pass to `Formatter` — T019 tests must pass
- [X] T021 Implement `src/credit_card_statement_extractor/transaction_extractor/__init__.py` — export public API: `Transaction`, `TransactionParser`, `DefaultParser`, `LocaleConfig`, `LOCALE_EN`, `LOCALE_PT_BR`, `Formatter`

**Checkpoint**: US1 + US2 both functional. Language flag controls all locale-specific output.

---

## Phase 5: User Story 3 — Graceful Handling of Unrecognised or Empty Statements (Priority: P3)

**Goal**: All error paths (no arg, bad file, non-PDF, no transactions, partial parse) produce clear stderr messages and correct exit codes; stdout is clean on failure.

**Independent Test**: Run with a PDF containing no transaction header — confirm "No transactions found" on stderr, exit 2, empty stdout.

### Tests for User Story 3

> **NOTE: Write tests FIRST — confirm they FAIL before proceeding to implementation.**

- [X] T022 Add US3 integration tests to `tests/integration/transaction_extractor/test_cli.py` — no argument → exit 1 + usage on stderr; missing file → exit 1 + "not found" on stderr; non-PDF (`tests/fixtures/pdfs/not_a_pdf.txt`) → exit 2 + "parse" on stderr; `no_transactions_statement.pdf` → exit 2 + "No transactions found" on stderr; `partial_statement.pdf` → exit 0 + "Warning: 2 line(s) could not be parsed" on stderr + 2-row table on stdout; stdout empty for all non-zero exits
- [X] T023 Add US3 unit tests to `tests/unit/transaction_extractor/test_parser.py` — partial parse: lines not matching transaction regex are skipped and counted; parse returns only valid transactions and raises no exception; total-line PDF (only header + totals row, no transaction rows) raises ValueError

### Implementation for User Story 3

- [X] T024 Update `src/credit_card_statement_extractor/transaction_extractor/_parser.py` — change `parse()` return type to `tuple[list[Transaction], int]` where int = number of skipped lines; update `_protocol.py` `TransactionParser` protocol signature to match the new return type; update `test_parser.py` (T006/T023 tests) to unpack the tuple; update `test_cli.py` (T013/T019/T022 tests) call sites — T023 tests must pass
- [X] T025 Update `src/credit_card_statement_extractor/transaction_extractor/__main__.py` — complete all error paths: no argument → usage + exit 1; `FileNotFoundError` → "File not found: <path>" + exit 1; PDF `ValueError` → "Could not parse as PDF: <path>" + exit 2; empty transaction list → "No transactions found in <path>" + exit 2; partial parse (unpack skip count from T024's updated `DefaultParser.parse()`) → "Warning: N line(s) could not be parsed and were skipped." to stderr, continue with exit 0; unhandled exception → "An unexpected error occurred. Please report this issue." + exit 3 — T022 tests must pass (depends on T024 complete)

**Checkpoint**: All three user stories functional. Full error handling in place per FR-010, FR-011, FR-012.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T026 [P] Add timing smoke test to `tests/integration/transaction_extractor/test_cli.py` — full CLI invocation on `en_statement.pdf` completes in < 2 s end-to-end (SC-001 / Constitution §V)
- [X] T027 Run `uv run pytest` — confirm all unit and integration tests pass with zero failures
- [X] T028 Run `uv run ruff check .` and `uv run ruff format .` — confirm zero linting or formatting violations
- [X] T029 Validate `quickstart.md` scenarios manually: English extraction, pt-BR extraction, and all error cases produce output matching the documented examples

---

## Phase 7: FR-013 — pt-BR Long Date Format Support

**Goal**: The parser correctly handles dates written as `14 de mar. 2026` (and `14 de mar 2026` without trailing period), as found in real Brazilian credit card statements.

**Independent Test**: Run `python -m credit_card_statement_extractor.transaction_extractor real_statement.pdf --lang pt-BR` where `real_statement.pdf` contains transactions with long pt-BR dates — confirm transactions are extracted with dates displayed in DD/MM/YYYY format.

### Fixture

- [ ] T030 Update `tests/fixtures/statements/create_fixtures.py` — add TWO new fixtures: (1) `ptbr_long_date_statement.pdf`: pt-BR headers (`Data Movimentação Valor`, NO Beneficiário column), 2 transactions with dates in long format (`14 de mar. 2026`) and amounts as raw numeric strings in pt-BR format (`- 85,91`); this fixture is used by Phase 7 tests only; (2) `ptbr_long_date_beneficiary_statement.pdf`: pt-BR headers (`Data Movimentação Beneficiário Valor`), 2 transactions with long dates and beneficiary values matching the real statement (`DrinksEBar`, `Posto de Gasolina`), amounts as `- 85,91` and `- 169,66`; this fixture is used by Phase 8 tests; regenerate all fixtures by re-running the script (T031)
- [ ] T031 Run `tests/fixtures/statements/create_fixtures.py` to regenerate fixtures including both new fixtures

### Tests for FR-013

> **NOTE: Write tests FIRST — confirm they FAIL before proceeding to implementation.**

- [ ] T032 [P] [US1] Add unit tests to `tests/unit/transaction_extractor/test_parser.py` — (a) `_parse_date` function: `"14 de mar. 2026"` → `date(2026, 3, 14)`; `"14 de mar 2026"` (no period) → `date(2026, 3, 14)`; all 12 month abbreviations parse to correct month numbers; unknown abbreviation raises `ValueError`; (b) `_normalise_amount` function: `"- R$ 85,91"` → `Decimal('-85.91')`; `"- R$ 1.234,56"` → `Decimal('-1234.56')`; plain `"85,91"` (no prefix) still works — confirming currency-prefix stripping does not break the existing path; (c) `DefaultParser.parse()` end-to-end: given a `PageResult` whose text contains `Data Movimentação Valor` header followed by a line `14 de mar. 2026  DrinksEBar  85,91`, the parser returns 1 transaction with `date(2026, 3, 14)` — confirming the full parse pipeline works for long-format dates; also test a `PageResult` with both a long-format and a numeric-format date on the same page to confirm both parse correctly (mixed-format edge case)
- [ ] T033 [US1] Add integration test to `tests/integration/transaction_extractor/test_cli.py` — run CLI on `ptbr_long_date_statement.pdf` (NO Beneficiário column) `--lang pt-BR`; confirm exit 0, dates appear as `14/03/2026` in output, transaction count matches fixture (2 transactions)

### Implementation for FR-013

- [ ] T034 [US1] Update `src/credit_card_statement_extractor/transaction_extractor/_parser.py` — three coordinated changes: (1) update `_TXN_RE` to add an alternation for the long pt-BR date prefix: `(\d{1,2} de \w+\.?\s+\d{4}|\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|\d{4}[/\-]\d{1,2}[/\-]\d{1,2})`; (2) update `_parse_date()` to try the long format first: detect via `" de "` in the string, strip trailing period from month token, map lowercase abbreviation to month number via a 12-entry dict (`jan`→1 … `dez`→12), raise `ValueError` for unknown abbreviation; fall through to existing numeric formats if no long-format match; (3) update `_normalise_amount()` to strip any leading currency prefix before parsing: remove optional `R\$\s*` or `\$\s*` prefix after the sign, so that `- R$ 85,91` normalises to `Decimal('-85.91')` — T032 tests must pass

**Checkpoint**: Statements with long pt-BR dates are parsed correctly.

---

## Phase 8: FR-014 — Beneficiário Column Support

**Goal**: When a statement has a `Beneficiário` column, its value is captured per transaction and displayed as an additional column in the output between Date and Description (or Descrição). Statements without this column are unaffected.

**Independent Test**: Run CLI on a fixture with a `Beneficiário` column — confirm the output table includes the Beneficiário/Beneficiary column; run on a fixture without it — confirm the column is absent.

### Tests for FR-014

> **NOTE: Write tests FIRST — confirm they FAIL before proceeding to implementation.**

- [ ] T035 [P] [US1] Add unit tests to `tests/unit/transaction_extractor/test_models.py` — `Transaction` with `beneficiary="DrinksEBar"` stores value correctly; `Transaction` without beneficiary (default) has `beneficiary=None`; frozen dataclass still raises on mutation; `Transaction.__post_init__` does not reject `None` beneficiary
- [ ] T036 [P] [US1] Add unit tests to `tests/unit/transaction_extractor/test_locale.py` — `LOCALE_EN` has `col_beneficiary="Beneficiary"`; `LOCALE_PT_BR` has `col_beneficiary="Beneficiário"`
- [ ] T037 [P] [US1] Add unit tests to `tests/unit/transaction_extractor/test_formatter.py` — `Formatter.render()` with `has_beneficiary=True`: output header contains "Beneficiário" (pt-BR) / "Beneficiary" (en) between date and description columns; with `has_beneficiary=False`: beneficiary column absent from header and all rows; beneficiary column is left-aligned with dynamic width
- [ ] T038 [US1] Add unit tests to `tests/unit/transaction_extractor/test_parser.py` — `DefaultParser.parse()` on header `"Data Movimentação Beneficiário Valor"`: returns transactions where `beneficiary` matches source values; `DefaultParser.parse()` on header without Beneficiário: all transactions have `beneficiary=None`; `_is_header_line()` recognises `"Beneficiário"` as a valid header token without confusing it for a description synonym

### Implementation for FR-014

- [ ] T039 [US1] Update `src/credit_card_statement_extractor/transaction_extractor/_models.py` — add `beneficiary: str | None = None` field to `Transaction` frozen dataclass (after `description`, before `amount`); update `__post_init__` to not validate beneficiary (None is valid) — T035 tests must pass
- [ ] T040 [US1] Update `src/credit_card_statement_extractor/transaction_extractor/_locale.py` — add `col_beneficiary: str` field to `LocaleConfig` dataclass; set `col_beneficiary="Beneficiary"` in `LOCALE_EN` and `col_beneficiary="Beneficiário"` in `LOCALE_PT_BR` — depends on T039; T036 tests must pass
- [ ] T041 [US1] Update `src/credit_card_statement_extractor/transaction_extractor/_parser.py` — in `_is_header_line()`: add `"beneficiário"` to a separate `_BENEFICIARY_HEADERS` frozenset (do NOT add to `_DESCRIPTION_HEADERS`); in `DefaultParser.parse()`: when scanning the header line, record the token index of the beneficiary header if present; during transaction-row parsing, split the row on `\s{2,}` and extract the token at that index as `beneficiary` (empty string if token missing); pass `beneficiary` to `Transaction()` constructor — T038 tests must pass
- [ ] T042 [US1] Update `src/credit_card_statement_extractor/transaction_extractor/_formatter.py` — `Formatter.render()` gains a `has_beneficiary: bool` parameter (default `False`); when `True`, insert beneficiary column between date and description columns using `locale.col_beneficiary` as header, dynamic width (min 12), left-aligned — T037 tests must pass
- [ ] T043 [US1] Update `src/credit_card_statement_extractor/transaction_extractor/__main__.py` — after `parser.parse()`, detect `has_beneficiary` by checking whether any `Transaction.beneficiary is not None`; pass `has_beneficiary` to `Formatter.render()`
- [ ] T044 [US1] Add integration tests to `tests/integration/transaction_extractor/test_cli.py` — (a) CLI on `ptbr_long_date_beneficiary_statement.pdf --lang pt-BR`: "Beneficiário" column present in stdout, beneficiary values `DrinksEBar` and `Posto de Gasolina` appear in output, dates appear as `14/03/2026`; (b) CLI on `ptbr_statement.pdf --lang pt-BR`: no "Beneficiário" column in stdout; (c) CLI on `en_statement.pdf`: no "Beneficiary" column in stdout

**Checkpoint**: Beneficiário column is captured and displayed when present; absent statements unaffected.

---

## Phase 9: Validation

- [ ] T045 [P] Run `uv run pytest` — confirm all unit and integration tests pass with zero failures
- [ ] T046 [P] Run `uv run ruff check .` and `uv run ruff format .` — confirm zero linting or formatting violations
- [ ] T047 Validate updated `quickstart.md` scenarios against actual CLI output: pt-BR with Beneficiário column, pt-BR without Beneficiário column, English output

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately ✅
- **Foundational (Phase 2)**: Depends on Phase 1 ✅
- **US1 (Phase 3)**: Depends on Phase 2 ✅
- **US2 (Phase 4)**: Depends on Phase 3 ✅
- **US3 (Phase 5)**: Depends on Phase 3 ✅
- **Polish (Phase 6)**: Depends on Phases 3–5 ✅
- **FR-013 (Phase 7)**: Depends on Phase 3 (extends `_parser.py` date handling); T031 depends on T030; T033 depends on T031; T034 depends on T032
- **FR-014 (Phase 8)**: Depends on Phase 7 (T030/T031 must run first to generate both fixtures); uses `ptbr_long_date_beneficiary_statement.pdf` (created in T030); T039 → T040 → T041 → T042 → T043 → T044; T035/T036/T037/T038 are parallel test tasks
- **Validation (Phase 9)**: Depends on Phases 7–8 complete

### Within Each Phase

- Test tasks written and confirmed **FAILING** before their implementation counterpart
- Models before services (`_models.py` before `_parser.py`)
- Protocol before concrete implementation (`_protocol.py` before `_parser.py`)
- Core components before CLI (`_parser.py`, `_formatter.py` before `__main__.py`)
- Within Phase 8: T039 (`_models.py`) → T040 (`_locale.py`) (sequential) → T041 (`_parser.py`) → T042 (`_formatter.py`) → T043 (`__main__.py`) → T044 (integration tests)

### Parallel Opportunities

- T001 and T002 are parallel (different directories)
- T006b and T006 can be written simultaneously after T005 (different test files; neither depends on T008)
- T007 can be written after T006c (_locale.py) in parallel with T006/T008 (different test file)
- T009 and T008 parallel within US1 (different source files)
- T015 and T016 parallel within US2 (test_locale.py vs. test_formatter.py extension)
- T026, T027, T028 parallel in Polish phase (independent validation steps)

---

## Parallel Example: User Story 1

```bash
# Write tests (both can be written simultaneously after T005):
Task T005: test_models.py
Task T007: test_formatter.py (skeleton, requires T006c first)

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
- `DefaultParser.parse()` return type changes in T024 (adds skip count) — all call sites updated as part of T024; T025 (__main__.py) depends on T024 completing first
- Statement fixture PDFs in `tests/fixtures/statements/` are the ground truth for parser correctness tests
- `_parser.py` header detection must recognise all variants documented in spec.md Clarifications
- Phase 7 (T034): Three coordinated changes — `_TXN_RE` updated to match long-date prefix; `_parse_date` updated to parse "DD de MMM. YYYY"; `_normalise_amount` updated to strip `R$ ` / `$ ` currency prefix from input amounts (e.g., `- R$ 85,91` → `Decimal('-85.91')`). All three must be done together
- Phase 8 (T041): `"Beneficiário"` belongs in `_BENEFICIARY_HEADERS` — NOT in `_DESCRIPTION_HEADERS`; header detection (`_is_header_line`) should NOT require a beneficiary column to validate a header row
- Phase 8 (T039): `Transaction.beneficiary` is an optional field with default `None`; frozen dataclass constraint still applies
- Phase 8 (T042/T043): `has_beneficiary` is derived at runtime from whether any parsed transaction has a non-None beneficiary; it is NOT passed as a CLI argument
