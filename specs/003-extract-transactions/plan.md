# Implementation Plan: Transaction Extractor

**Branch**: `003-extract-transactions` | **Date**: 2026-04-14 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/003-extract-transactions/spec.md`

## Summary

Extend the existing `transaction_extractor` module — which already handles numeric date formats and a fixed three-column (date / description / amount) table — to correctly parse real Brazilian Portuguese statements that use:

1. A pt-BR long date format: `DD de MMM. YYYY` (e.g., `14 de mar. 2026`) — FR-013
2. A distinct, optional `Beneficiário` column between date and description — FR-014

Both gaps were discovered during integration testing against the real statement file. The implementation updates the parser, data model, formatter, locale config, CLI output, and all affected tests. No new dependencies required; stdlib only.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: `pdfplumber ≥ 0.11` (via `pdf_reader`); stdlib only for new code (`re`, `datetime`, `decimal`)  
**Storage**: N/A — file system read-only  
**Testing**: `pytest`; `ruff` for lint/format  
**Target Platform**: macOS / Linux (developer workstation + CI)  
**Project Type**: CLI tool / library  
**Performance Goals**: Single statement extraction < 2 seconds (Constitution §V; unchanged)  
**Constraints**: No new production dependencies; stdlib only  
**Scale/Scope**: Single-statement, single-process invocation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality | PASS | Changes are surgical: parser regex + date parser + model field + formatter branch. Each touched unit has a single responsibility. |
| II. Test-First | PASS | Plan mandates TDD: failing tests for FR-013 and FR-014 written first. |
| III. Testing Standards | PASS | New unit tests for `_parse_date` long-format path and `Formatter` beneficiary column. Integration fixture using the real sample statement. |
| IV. UX Consistency | PASS | CLI contract extended: beneficiary column present only when source has it; stderr/stdout/exit code semantics unchanged. |
| V. Performance | PASS | Single extra regex alternative + one optional dict lookup — negligible overhead. |
| VI. Simplicity | PASS | No new abstractions; existing `_parse_date`, `Transaction`, `LocaleConfig`, `Formatter` extended minimally. YAGNI respected — no general column-mapping framework. |
| Data & Security | PASS | No logging of raw statement content; changes are pure parsing logic. |

**Post-design re-check**: All gates still PASS after Phase 1 design (see below).

## Project Structure

### Documentation (this feature)

```text
specs/003-extract-transactions/
├── plan.md              # This file
├── research.md          # Phase 0 output (existing, updated below)
├── data-model.md        # Phase 1 output (updated)
├── quickstart.md        # Phase 1 output (updated)
├── contracts/
│   └── cli-contract.md  # Phase 1 output (updated)
└── tasks.md             # Phase 2 output (/speckit.tasks — NOT created here)
```

### Source Code

```text
src/credit_card_statement_extractor/transaction_extractor/
├── __init__.py          # no change
├── __main__.py          # minor: pass has_beneficiary flag to Formatter
├── _formatter.py        # extend: optional beneficiary column
├── _locale.py           # extend: col_beneficiary field on LocaleConfig
├── _models.py           # extend: optional beneficiary field on Transaction
├── _parser.py           # extend: long date regex + currency-prefix amount stripping + beneficiary column detection
└── _protocol.py         # no change (return type already tuple[list[Transaction], int])

tests/
├── unit/transaction_extractor/
│   ├── test_parser.py       # new tests: long date, beneficiary column
│   ├── test_formatter.py    # new tests: beneficiary column present/absent
│   └── test_locale.py       # update: col_beneficiary field
└── integration/
    └── transaction_extractor/test_cli.py   # fixture: real sample statement
```

**Structure Decision**: Single project layout (already established). No new files or directories beyond existing `tests/unit/transaction_extractor/` and `tests/integration/`.

## Complexity Tracking

No constitution violations. No complexity justification required.
