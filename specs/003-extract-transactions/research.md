# Research: Transaction Extractor

**Feature**: 003-extract-transactions | **Date**: 2026-04-12

## Decision 1: Parsing strategy — regex line-by-line vs. pdfplumber table extraction

**Decision**: Regex-based line-by-line parsing.

**Rationale**: `pdfplumber` exposes two text extraction modes — `extract_text()` (plain text, already used by `pdf_reader`) and `extract_table()` (structured rows using PDF layout heuristics). Table extraction works best with clearly bordered tables and consistent column spacing. Real-world credit card statements frequently use mixed layouts — titles, summaries, and transaction blocks on the same page — making table extraction fragile without fine-tuned bounding-box parameters that are statement-format-specific. Line-by-line regex on the existing `PageResult.text` field requires no additional pdfplumber API surface, keeps the `pdf_reader` abstraction intact, and gives full control over the matching logic.

**Alternatives considered**:
- `pdfplumber.extract_table()`: Rejected — requires per-format bounding-box tuning; brittle against layout variations.
- `pdfminer.six` directly: Rejected — already available transitively but bypasses the `pdf_reader` abstraction established in feature 002.
- `pandas.read_csv` / tabula-py: Rejected — additional dependencies violate §VI and constitution no-new-deps constraint.

---

## Decision 2: Locale formatting — stdlib `locale` module vs. custom `LocaleConfig`

**Decision**: Custom `LocaleConfig` frozen dataclass (stdlib only).

**Rationale**: Python's `locale` module configures process-wide state via `locale.setlocale()`, which is non-thread-safe and depends on the host OS having the target locale installed (`pt_BR.UTF-8` may not be present on CI machines or developer workstations). A `LocaleConfig` dataclass with explicit fields (`date_format`, `decimal_separator`, `thousands_separator`, `currency_prefix`, `col_date`, `col_description`, `col_amount`) is fully portable, testable with no side effects, and trivially extensible to new locales.

**Alternatives considered**:
- `locale.setlocale` + `locale.format_string`: Rejected — process-global state, OS-dependent availability, non-thread-safe.
- Babel library: Rejected — adds a production dependency for functionality expressible in ~30 lines of stdlib code (§VI YAGNI).

---

## Decision 3: Amount parsing — detecting pt-BR vs. English decimal format in raw text

**Decision**: Heuristic based on the last numeric separator before the digits at the end of the amount string.

**Rationale**: When pdfplumber extracts statement text, the amount appears as a raw string like `1.234,56` (pt-BR) or `1,234.56` (English). The canonical rule: if the string ends with `,[digits]{1,2}`, the comma is the decimal separator (pt-BR); if it ends with `.[digits]{1,2}`, the period is the decimal separator (English). Any remaining separators are thousands separators and are stripped. This heuristic handles all common real-world Brazilian bank formats without requiring locale-aware parsing.

**Alternatives considered**:
- Require the user to pass `--lang` for parsing too (not just display): Rejected — the spec and clarifications specify `--lang` controls display only; parsing should be format-agnostic.
- Always parse as English and convert: Rejected — fails on `1.234,56` (would misparse as `1.234` plus junk).

---

## Decision 4: Fixed-width column widths — static vs. dynamic

**Decision**: Dynamic column widths — compute max content length per column across all rows, enforce minimum widths (date: 10, description: 20, amount: 12).

**Rationale**: Static widths would either truncate long descriptions or waste horizontal space on short ones. Dynamic widths adapt to the data while minimum floors ensure the header labels always fit. Column widths are computed once before rendering.

**Alternatives considered**:
- Static widths (e.g., 10 / 40 / 15): Rejected — truncates or wastes space depending on statement content.
- `tabulate` or `rich` library: Rejected — adds a production dependency for straightforward string formatting (§VI).

---

## Decision 5: Transaction table boundary detection

**Decision**: Scan all lines for a header row containing at least one recognised column label from each of the three groups (date, description, amount). Lines from that row onward that match the transaction regex are parsed as transactions. Parsing stops at the first line that matches a "totals" sentinel (e.g., starts with "Total" or "Saldo") or a blank section separator (2+ consecutive empty lines after the first transaction).

**Rationale**: Credit card statements contain non-transaction text (titles, account info, totals). Using the header row as the start sentinel and structural blanks / totals as the end sentinel covers the common layouts without requiring format-specific column position knowledge.

**Recognised header labels** (from clarifications):
- Date: `"Data"`, `"Data da Compra"`, `"Data Lançamento"`, `"Date"`
- Description: `"Descrição"`, `"Histórico"`, `"Movimentação"`, `"Estabelecimento"`, `"Description"`
- Amount: `"Valor"`, `"Valor (R$)"`, `"Amount"`

**Transaction line regex**:
```
^(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\s+(.+?)\s{2,}([+\-]?\d[\d.,]*)$
```
(two or more spaces before the amount field to avoid greedily consuming trailing description words)

---

## Decision 6: Date parsing — multiple format attempts

**Decision**: Try date formats in priority order: `%d/%m/%Y` → `%Y-%m-%d` → `%m/%d/%Y` → `%d/%m/%y`. First successful parse wins. Raise `ValueError` if none match.

**Rationale**: The same parser handles both English and pt-BR source PDFs. Trying the most common pt-BR format first minimises the risk of ambiguous dates (e.g., `01/03/2026` parsed as January 3 instead of March 1 under `%m/%d/%Y`). ISO 8601 format is unambiguous and checked second.

---

## Decision 7: Exit code mapping

| Condition | Exit code | Notes |
|-----------|-----------|-------|
| Success (≥1 transaction printed) | 0 | |
| No file argument provided | 1 | User error |
| File not found | 1 | User error |
| File is not a valid PDF | 2 | Parse failure (reuses pdf_reader error code) |
| No transactions found in PDF | 2 | Parse failure (FR-010) |
| Unexpected internal error | 3 | Constitution §IV |

Partial parse (some lines skipped) prints a warning to stderr but exits 0 (FR-011).
