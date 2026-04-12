# Quickstart: PDF Reader Module

## Prerequisites

- Python 3.11+
- `uv` installed

## Install

```shell
uv sync --all-extras
```

This installs `pdfplumber` (and its `pdfminer.six` dependency) along with all dev dependencies.

## Run

```shell
python -m credit_card_statement_extractor.pdf_reader path/to/statement.pdf
```

Expected output (truncated example):

```
--- Page 1 ---
ACCOUNT SUMMARY
Statement Date: March 31 2026
...

--- Page 2 ---
TRANSACTIONS
03/01  Coffee Shop           4.50
...
```

## Run Tests

```shell
uv run pytest
```

## Swap the PDF Library

To substitute an alternative reader (e.g., `pypdf`):

1. Create a new class in `src/credit_card_statement_extractor/pdf_reader/` that implements the `PDFReader` protocol (i.e., provides `read(path: Path) -> list[PageResult]`).
2. In the module's `__main__.py`, replace the instantiation of `PdfplumberReader` with your new class.
3. No other files need to change.

The CLI interface, output format, and tests remain identical.
