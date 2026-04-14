# Data Model: Export Transactions to CSV and XLSX

**Feature**: 004-export-csv-xlsx  
**Date**: 2026-04-14

---

## Existing Entities (unchanged)

### Transaction
Already defined in `_models.py`. No changes required for this feature.

| Field | Type | Notes |
|-------|------|-------|
| `date` | `datetime.date` | Parsed from PDF |
| `description` | `str` | Non-empty, strip-validated |
| `amount` | `decimal.Decimal` | Signed; negative = debit |
| `beneficiary` | `str \| None` | Optional; None when column absent |

### LocaleConfig
Already defined in `_locale.py`. No changes required for this feature.

| Field | Type | Notes |
|-------|------|-------|
| `code` | `str` | `"en"` or `"pt-BR"` |
| `date_format` | `str` | strftime format |
| `decimal_separator` | `str` | `.` or `,` |
| `thousands_separator` | `str` | `,` or `.` |
| `currency_prefix` | `str` | `""` or `"R$ "` |
| `col_date` | `str` | Column header label |
| `col_description` | `str` | Column header label |
| `col_amount` | `str` | Column header label |
| `col_beneficiary` | `str` | Column header label |

---

## New Entity: ExportConfig

A lightweight value object capturing the parameters for a single export operation. Not persisted; constructed in `__main__.py` and passed to `Exporter`.

| Field | Type | Notes |
|-------|------|-------|
| `path` | `pathlib.Path` | Absolute or relative output path |
| `format` | `Literal["csv", "xlsx"]` | Derived from `path.suffix.lower()` |
| `has_beneficiary` | `bool` | True if any transaction has non-None beneficiary |

**Validation rules**:
- `path.suffix.lower()` must be `".csv"` or `".xlsx"` — else raise `ValueError`
- `path.parent` must exist as a directory — else raise `FileNotFoundError`

---

## Column Mapping

The export columns are derived from the same source as the formatter, ensuring consistency:

| Column | CSV header (en) | CSV header (pt-BR) | CSV value | XLSX type |
|--------|-----------------|--------------------|-----------|-----------|
| Date | `Date` | `Data` | `locale.date_format` string | `datetime.date` (native) |
| Beneficiary | `Beneficiary` | `Beneficiário` | `str` (or omitted if `has_beneficiary=False`) | `str` |
| Description | `Description` | `Descrição` | `str` | `str` |
| Amount | `Amount` | `Valor` | decimal string with `.` separator, e.g. `-4.50` | `float` or `Decimal` (numeric) |

**Amount in CSV**: Always dot-decimal, no currency symbol, no thousands separator. Example: `-4.50`, `500.00`, `-1234.56`.

**Amount in XLSX**: Stored as a native numeric type. Display formatting applied via xlsxwriter number format `#,##0.00` (locale-neutral cell format, letting Excel's regional settings control display).

---

## File Artifacts (not domain entities)

| Artifact | Location | Created by |
|----------|----------|------------|
| `transactions.csv` | User-specified `--output` path | `CsvWriter._write()` |
| `transactions.xlsx` | User-specified `--output` path | `XlsxWriter._write()` |
