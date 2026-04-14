# credit-card-statement-extractor Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-14

## Active Technologies
- Python 3.11+ + `pdfplumber` (text extraction); `pdfminer.six` (transitive, pulled by pdfplumber) (feat/002-pdf-reader)
- N/A — file system read-only (feat/002-pdf-reader)
- Python 3.11+ + `pdfplumber ≥ 0.11` (via `pdf_reader`); stdlib only for new code (`re`, `datetime`, `decimal`) (003-extract-transactions)
- Python 3.11+ + `pdfplumber ≥ 0.11` (existing); `xlsxwriter ≥ 3.0` (new, optional `xlsx` extra); stdlib `csv`, `pathlib`, `datetime`, `decimal` (no new mandatory deps) (004-export-csv-xlsx)
- File system write — single output file per invocation (004-export-csv-xlsx)
- File system write — single output file per invocation, in same directory as input PDF (004-export-csv-xlsx)

- Python 3.11+ + `hatchling` (build), `uv` (dependency manager + venv), `pytest` (test), `ruff` (lint/format) (main)

## Project Structure

```text
src/
tests/
```

## Commands

```shell
uv sync --all-extras   # install deps and create .venv
uv run pytest          # run tests
uv run ruff check .    # lint
uv run ruff format .   # format
```

## Code Style

Python 3.11+: Follow standard conventions

## Recent Changes
- 004-export-csv-xlsx: Added Python 3.11+ + `pdfplumber ≥ 0.11` (existing); `xlsxwriter ≥ 3.0` (new, optional `xlsx` extra); stdlib `csv`, `pathlib`, `datetime`, `decimal` (no new mandatory deps)
- 004-export-csv-xlsx: Added Python 3.11+ + `pdfplumber ≥ 0.11` (existing); `xlsxwriter ≥ 3.0` (new, optional `xlsx` extra); stdlib `csv`, `pathlib`, `datetime`, `decimal` (no new mandatory deps)
- 003-extract-transactions: Added Python 3.11+ + `pdfplumber ≥ 0.11` (via `pdf_reader`); stdlib only for new code (`re`, `datetime`, `decimal`)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
