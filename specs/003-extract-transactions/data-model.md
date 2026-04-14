# Data Model: Transaction Extractor

**Feature**: 003-extract-transactions | **Date**: 2026-04-12

---

## Entity: `Transaction`

A single financial event parsed from a credit card statement.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `date` | `datetime.date` | Required | Parsed from statement; format-agnostic at storage level |
| `description` | `str` | Required; non-empty after strip | Merchant name or transaction narrative |
| `amount` | `decimal.Decimal` | Required | Positive = purchase/charge; Negative = payment/credit/refund |
| `beneficiary` | `str \| None` | Optional; default `None` | Present only when source statement includes a "Beneficiário" column (FR-014) |

**Frozen dataclass** (`frozen=True`): immutable after construction; safe to cache or hash.

**Validation rules**:
- `description` must not be empty after stripping whitespace.
- `amount` precision is preserved from the source string (e.g., `-49.90` stored as `Decimal('-49.90')`).
- No restriction on `amount` sign — both positive and negative values are valid.
- `beneficiary` may be `None` (column absent) or an empty string (column present but cell blank); both are valid.

**No identity key**: Two transactions may share the same date and description (e.g., two identical coffee purchases). Order is preserved as-read (FR-005).

---

## Entity: `LocaleConfig`

Display configuration for a single output language/region.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `code` | `str` | Required; e.g., `"en"`, `"pt-BR"` | Language tag |
| `date_format` | `str` | Required; strftime format string | `"%Y-%m-%d"` for en; `"%d/%m/%Y"` for pt-BR |
| `decimal_separator` | `str` | Required; single char | `"."` for en; `","` for pt-BR |
| `thousands_separator` | `str` | Required; single char | `","` for en; `"."` for pt-BR |
| `currency_prefix` | `str` | Required; may be empty | `""` for en; `"R$ "` for pt-BR |
| `col_date` | `str` | Required | Column header label for Date column |
| `col_description` | `str` | Required | Column header label for Description column |
| `col_amount` | `str` | Required | Column header label for Amount column |
| `col_beneficiary` | `str` | Required | Column header label for Beneficiary column (used only when column is present); English: `"Beneficiary"`, pt-BR: `"Beneficiário"` |

**Frozen dataclass**. Two pre-built instances exported from `_locale.py`:
- `LOCALE_EN`: English defaults (ISO date, no currency prefix)
- `LOCALE_PT_BR`: Brazilian Portuguese (DD/MM/YYYY, R$ prefix, comma decimal)

---

## Protocol: `TransactionParser`

Structural interface for pluggable parsers (mirrors `PDFReader` pattern from feature 002).

```
TransactionParser.parse(pages: list[PageResult]) -> tuple[list[Transaction], int]
```

- Input: one `PageResult` per page from the `pdf_reader` module.
- Output: `(transactions, skipped_count)` — ordered list of `Transaction` objects plus the number of unrecognised lines after the header.
- Raises `ValueError` if no transaction table header is found.
- `Transaction.beneficiary` is populated when the source statement includes a `"Beneficiário"` column; `None` otherwise.

**Concrete implementation** (this feature): `DefaultParser` in `_parser.py`.

To support a new statement format: implement this protocol and pass the new parser to the CLI (or extend `DefaultParser` with additional header variants).

---

## Relationships

```
PDFReader ──reads──► list[PageResult]
                          │
                          ▼
              TransactionParser.parse()
                          │
                          ▼
                  list[Transaction]
                          │
                          ▼
              Formatter(locale: LocaleConfig)
                          │
                          ▼
                   stdout (table)
```

---

## State & Lifecycle

All entities are immutable value objects. There is no persistence layer — data flows linearly from PDF input to stdout output within a single process invocation.
