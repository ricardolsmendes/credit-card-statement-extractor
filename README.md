# Credit Card Statement Extractor

A CLI tool that extracts transactions from credit card statement PDFs and exports them as a
formatted table, CSV, or XLSX file. Built as a learning project to explore
[Claude Code](https://claude.ai/code) and [GitHub Speckit](https://github.com/github/spec-kit)
as primary development tools.

## Installation

**Prerequisites**: Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/ricardomendes/credit-card-statement-extractor.git
cd credit-card-statement-extractor
uv sync --all-extras
```

> **XLSX support** requires the optional `xlsxwriter` extra (included with `--all-extras`).
> If you only need CSV output: `uv sync` (no extras needed).

**Alternative (pip)**:
```bash
pip install -e .
```

## Usage

### Print transactions to the terminal

```bash
python -m credit_card_statement_extractor.transaction_extractor statement.pdf
```

```
Date        Description                 Amount
----------------------------------------------
2026-03-01  Coffee Shop                  -4.50
2026-03-02  Grocery Store               -82.10
2026-03-10  Payment received           +500.00
2026-03-15  Gas Station                 -89.50
```

### Export to CSV

```bash
python -m credit_card_statement_extractor.transaction_extractor statement.pdf --output-format csv
```

```
Exported 4 transactions to statement-transactions.csv
```

The output file `statement-transactions.csv` is created in the same directory as the input PDF:

```
Date,Description,Amount
2026-03-01,Coffee Shop,-4.50
2026-03-02,Grocery Store,-82.10
2026-03-10,Payment received,500.00
2026-03-15,Gas Station,-89.50
```

### Export to XLSX

```bash
python -m credit_card_statement_extractor.transaction_extractor statement.pdf --output-format xlsx
```

```
Exported 4 transactions to statement-transactions.xlsx
```

The XLSX file is created next to the input PDF with native date and numeric cell types.

### Brazilian Portuguese output

```bash
python -m credit_card_statement_extractor.transaction_extractor faturas.pdf \
  --lang pt-BR --output-format csv
```

Column headers and date format follow the pt-BR locale (`Data`, `Descrição`, `Valor`;
dates as `DD/MM/YYYY`).

## CLI Reference

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `file_path` | positional | — | Path to the PDF credit card statement |
| `--lang` | option | `en` | Output language: `en` or `pt-BR` |
| `--output-format` | option | — | Export format: `csv` or `xlsx`. Omit to print a formatted table to stdout |

**Exit codes**: `0` success · `1` user error (file not found, write error) · `2` parse failure (no transactions found) · `3` internal error

## Developer's Guide

### Development Tools

This project uses two AI-assisted development tools throughout its entire workflow:

- **[Claude Code](https://claude.ai/code)** — AI-powered CLI that writes, edits, and runs code
  from natural language instructions. Used for all implementation tasks: writing source code,
  tests, and documentation.

- **[GitHub Speckit](https://github.com/github/spec-kit)** — Specification-driven development
  workflow tool. Used to write feature specifications, generate implementation plans, and produce
  TDD task breakdowns *before* any code is written. Every feature in this project follows the
  Speckit workflow: `specify → clarify → plan → tasks → analyze → implement`.

### Development Commands

```bash
uv sync --all-extras     # install all dependencies (including xlsxwriter and dev tools)
uv run pytest            # run the full test suite
uv run ruff check .      # lint
uv run ruff format .     # format
```
