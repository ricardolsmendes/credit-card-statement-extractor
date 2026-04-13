# Implementation Plan: PDF Reader Module

**Branch**: `002-pdf-reader` | **Date**: 2026-04-12 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/002-pdf-reader/spec.md`

## Summary

Add a swappable PDF text-extraction module to the project. The initial implementation uses `pdfplumber` for layout-aware text extraction from digitally-generated credit card statement PDFs. A `PDFReader` Protocol defines the reader interface, ensuring the underlying library can be replaced by modifying a single file. A `python -m` entry point accepts a file path argument, prints page-separated text to stdout, and writes errors to stderr with meaningful exit codes.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: `pdfplumber` (text extraction); `pdfminer.six` (transitive, pulled by pdfplumber)  
**Storage**: N/A — file system read-only  
**Testing**: pytest  
**Target Platform**: Developer workstation (macOS/Linux)  
**Project Type**: CLI tool / library module  
**Performance Goals**: Full extraction of a 50-page PDF in under 5 seconds  
**Constraints**: No raw statement content in logs; memory usage scales with page count (lazy iteration); no external network calls  
**Scale/Scope**: Single-file input; single developer usage for verification

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Gate | Principle | Status | Notes |
|------|-----------|--------|-------|
| TDD enforced | §II Test-First | PASS | Tests written before implementation; fixtures use real sample PDFs |
| Single responsibility | §I Code Quality | PASS | Reader module does one thing; CLI and formatting are separate |
| No speculative features | §VI Simplicity | PASS | No OCR, caching, batch processing, or output files |
| No raw content in logs | §Data & Security | PASS | Only metadata (path, page count) logged; raw text never logged |
| CLI contract is primary interface | §IV UX Consistency | PASS | stdout for output, stderr for errors, exit codes per convention |
| Memory scales linearly | §V Performance | PASS | Pages iterated lazily via `pdfplumber.pages` |
| Dependency justified | §VI Simplicity | PASS | `pdfplumber` is the only new dependency; chosen over pypdf for layout fidelity on statement PDFs |
| No silent failures | §IV UX Consistency | PASS | All error paths produce stderr output and non-zero exit codes |

**Post-design re-check**: All gates still pass. The Protocol pattern adds zero runtime complexity; no violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/002-pdf-reader/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── cli-contract.md  # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks — not created here)
```

### Source Code (repository root)

```text
src/credit_card_statement_extractor/
├── __init__.py                   # existing
└── pdf_reader/
    ├── __init__.py               # exports PDFReader, PageResult, PdfplumberReader
    ├── _protocol.py              # PDFReader Protocol + PageResult dataclass
    ├── _pdfplumber_reader.py     # PdfplumberReader — concrete implementation
    └── __main__.py               # CLI entry point (python -m ...pdf_reader)

tests/
├── unit/
│   └── pdf_reader/
│       ├── test_protocol.py           # PageResult construction, type checks
│       └── test_pdfplumber_reader.py  # extraction, multi-page, error paths
├── integration/
│   └── pdf_reader/
│       └── test_cli.py                # subprocess invocation tests
└── fixtures/
    └── pdfs/
        ├── single_page.pdf            # minimal single-page fixture
        ├── multi_page.pdf             # 2+ page fixture
        └── not_a_pdf.txt              # invalid input fixture
```

**Structure Decision**: Single-project layout (Option 1). The `pdf_reader` sub-package groups protocol, implementation, and entry point together. This makes swapping the reader a one-file change (`_pdfplumber_reader.py` → new file + update `__main__.py` import).

## Complexity Tracking

No constitution violations. No complexity justification required.
