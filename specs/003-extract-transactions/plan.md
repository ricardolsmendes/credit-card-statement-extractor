# Implementation Plan: Transaction Extractor

**Branch**: `003-extract-transactions` | **Date**: 2026-04-12 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-extract-transactions/spec.md`

## Summary

Builds a transaction extraction layer on top of the existing `pdf_reader` module. Raw page text is scanned for a recognised column-header row; subsequent lines matching a date + description + amount pattern are parsed into `Transaction` records. Results are rendered as a fixed-width, locale-aware table to stdout. Supports English (default) and Brazilian Portuguese via `--lang en` / `--lang pt-BR`.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: `pdfplumber ≥ 0.11` (via `pdf_reader`); stdlib only for new code (`re`, `datetime`, `decimal`)
**Storage**: N/A — file system read-only
**Testing**: pytest ≥ 8.0
**Target Platform**: Developer workstation (macOS/Linux)
**Project Type**: CLI tool / library module
**Performance Goals**: End-to-end extraction < 2 s (SC-001; parsing step adds negligible time over pdf_reader baseline)
**Constraints**: No new production dependencies; stdlib only for parsing and formatting
**Scale/Scope**: Single statement per invocation, up to 50 pages

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| §I Code Quality | ✓ PASS | Each module has a single responsibility; complexity earns its place |
| §II Test-First | ✓ PASS | TDD enforced — tests written and confirmed failing before implementation |
| §III Testing Standards | ✓ PASS | Unit: parser / formatter / locale; Integration: full pipeline; fixtures over mocks |
| §IV UX Consistency | ⚠ JUSTIFIED DEVIATION | See below |
| §V Performance | ✓ PASS | Parsing step is O(n lines); dominated by pdf_reader (< 2 s) |
| §VI Simplicity | ✓ PASS | No new deps; Protocol abstraction justified by explicit multi-format requirement in Assumptions |
| Data Security | ✓ PASS | Raw statement text never logged |

**§IV Deviation — fixed-width table instead of JSON default**: The approved spec (FR-004, clarification Q2) explicitly requires a fixed-width aligned table. The spec also states "there is no need to build a complex CLI interface at this point." Adding JSON as the default output contradicts the approved spec and violates §VI (YAGNI). JSON output is deferred to a future feature.

## Project Structure

### Documentation (this feature)

```text
specs/003-extract-transactions/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/credit_card_statement_extractor/
├── __init__.py                              (unchanged)
├── pdf_reader/                              (unchanged — feature 002)
└── transaction_extractor/                   (new — feature 003)
    ├── __init__.py                          (public API: Transaction, TransactionParser, DefaultParser)
    ├── __main__.py                          (CLI: python -m ... <file> [--lang en|pt-BR])
    ├── _models.py                           (Transaction frozen dataclass)
    ├── _protocol.py                         (TransactionParser Protocol)
    ├── _parser.py                           (default concrete parser — header detection + row parsing)
    ├── _locale.py                           (LocaleConfig; en + pt-BR instances)
    └── _formatter.py                        (fixed-width table renderer)

tests/
├── fixtures/
│   ├── pdfs/                                (existing — feature 002)
│   └── statements/                          (new — realistic statement PDFs for feature 003)
│       ├── create_fixtures.py               (generates en_statement.pdf + ptbr_statement.pdf)
│       ├── en_statement.pdf                 (English-format statement with known transactions)
│       └── ptbr_statement.pdf               (pt-BR-format statement with known transactions)
├── unit/
│   ├── pdf_reader/                          (existing — feature 002)
│   └── transaction_extractor/               (new)
│       ├── __init__.py
│       ├── test_models.py                   (Transaction dataclass validation)
│       ├── test_parser.py                   (header detection, row parsing, error paths)
│       ├── test_locale.py                   (date / amount formatting per locale)
│       └── test_formatter.py                (fixed-width table rendering)
└── integration/
    ├── pdf_reader/                          (existing — feature 002)
    └── transaction_extractor/               (new)
        ├── __init__.py
        └── test_cli.py                      (full end-to-end CLI tests)
```

**Structure Decision**: Mirrors the `pdf_reader` sub-package layout established in feature 002. Single-project layout extended with a new `transaction_extractor` sub-package. Test tree mirrors the source tree.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| §IV: Table output instead of JSON default | Spec FR-004 + clarification Q2 explicitly require fixed-width table | JSON would contradict the approved spec and violate YAGNI (§VI) |
| Protocol abstraction (`TransactionParser`) | Spec Assumptions mandate that additional formats can be added without rewriting core logic | A single class with no protocol would require rewriting callers when new formats are added |
