# Research: Export Transactions to CSV and XLSX

**Feature**: 004-export-csv-xlsx  
**Date**: 2026-04-14

---

## Decision 1: XLSX Library

**Decision**: Use `xlsxwriter` (BSD-2-Clause, zero dependencies, ~1.2 MB)

**Rationale**:
- Pure Python, zero transitive dependencies (openpyxl requires `et-xmlfile`)
- Write-only API is exactly what a CLI export needs; no read/modify overhead
- Handles `datetime.date` and `decimal.Decimal` natively
- UTF-8 with accented characters (pt-BR) works correctly
- Actively maintained, supports Python 3.8–3.13

**Alternatives considered**:
- `openpyxl` — viable but heavier (bi-directional read/write, extra dep); ruled out by YAGNI since we never need to read XLSX files
- `xlwt` — generates obsolete Excel 97 `.xls` format; ruled out
- `odfpy` — generates ODS (LibreOffice), not XLSX; ruled out

**Added as optional extra**: `xlsxwriter` will be declared under `[project.optional-dependencies]` as `xlsx` extra in `pyproject.toml`. The CSV exporter uses only stdlib and requires no extra install.

---

## Decision 2: CSV Encoding and Format

**Decision**: UTF-8 with BOM (`encoding="utf-8-sig"`), comma delimiter, stdlib `csv` module

**Rationale**:
- `utf-8-sig` ensures correct display of accented characters (é, ã, ç) when opened in Excel on Windows; negligible overhead
- Python stdlib `csv` module handles RFC 4180 quoting automatically; no third-party library needed
- Comma delimiter is universally correct for `.csv`; locale decimal format does NOT affect delimiter choice

**Amount representation in CSV**: Always write amounts with dot as decimal separator (e.g., `-4.50`), regardless of `--lang`. CSV is a data interchange format — let the consuming application apply locale formatting. Currency symbols and thousands separators are omitted.

**Date representation in CSV**: Written as text strings using the locale's `date_format` (e.g., `2026-03-01` for `en`, `01/03/2026` for `pt-BR`). This matches user expectation of locale-consistent column values.

---

## Decision 3: Integration Architecture

**Decision**: New `_exporter.py` module inside `transaction_extractor`, parallel to `_formatter.py`

**Rationale**:
- Single Responsibility: keeps export logic separate from display formatting
- The exporter operates on the same `list[Transaction]` + `LocaleConfig` inputs as `Formatter.render()`
- Public interface: `Exporter.export(transactions, locale, path, has_beneficiary)` — returns nothing, writes the file
- Format dispatching is by file extension (`.csv` → CSV writer, `.xlsx` → XLSX writer)
- Both writers share a column-header and row-data builder so column order is consistent

**`__main__.py` change**: Add `--output <path>` argument. When present:
- Call `Exporter.export(...)` instead of `Formatter.render()`
- Print confirmation to stdout (`Exported N transactions to <path>`)
- Suppress the table output

**No new subpackage**: The exporter lives at the same level as `_formatter.py`. A dedicated `exporters/` subpackage would be premature abstraction (Constitution §VI).

---

## Decision 4: Dependency Declaration

**Decision**: `xlsxwriter` declared as an optional `xlsx` extra in `pyproject.toml`; CSV export works with no extras

```toml
[project.optional-dependencies]
xlsx = ["xlsxwriter>=3.0"]
dev = ["pytest>=8.0", "ruff>=0.4"]
```

**Rationale**: Constitution §VI (YAGNI / dependencies are liabilities). Users who only need CSV should not be forced to install xlsxwriter. The CLI prints a clear error if `--output file.xlsx` is requested but xlsxwriter is not installed.

---

## Decision 5: Error Handling for `--output`

- Parent directory does not exist → stderr error, exit 1
- Unrecognised file extension → stderr error, exit 1
- Permission denied → stderr error, exit 1  
- `xlsxwriter` not installed for `.xlsx` output → stderr error with install hint, exit 1
- Zero transactions → no file written (existing exit 2 path fires first)
