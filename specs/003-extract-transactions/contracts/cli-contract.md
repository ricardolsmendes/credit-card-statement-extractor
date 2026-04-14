# CLI Contract: Transaction Extractor

**Feature**: 003-extract-transactions | **Date**: 2026-04-14 (updated: long date format + Beneficiário column)

---

## Command

```
python -m credit_card_statement_extractor.transaction_extractor <file_path> [--lang <code>]
```

---

## Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `file_path` | positional | Yes | — | Path to the PDF credit card statement |
| `--lang` | optional flag | No | `en` | Output language code. Accepted values: `en`, `pt-BR` |

---

## Exit Codes

| Code | Meaning | Trigger condition |
|------|---------|-------------------|
| `0` | Success | At least one transaction was extracted and printed |
| `1` | User error | No file argument provided, or file path does not exist |
| `2` | Parse failure | File is not a valid PDF, or no transactions found in PDF |
| `3` | Internal error | Unexpected exception not caused by user input |

---

## Standard Output (exit 0)

A fixed-width table printed to stdout. Format (English example, no beneficiary column):

```
Date        Description                    Amount
----------  -----------------------------  -----------
2026-03-01  Coffee Shop                         -4.50
2026-03-02  Grocery Store                      -82.10
2026-03-10  Payment received                  +500.00
```

Brazilian Portuguese example with beneficiary column (`--lang pt-BR`):

```
Data        Beneficiário              Descrição                      Valor
----------  ------------------------  -----------------------------  -----------
14/03/2026  DrinksEBar                                          -R$ 85,91
14/03/2026  Posto de Gasolina                                      -R$ 169,66
```

**Formatting rules**:
- First row: column labels in selected language (FR-009).
- Second row: separator line of `-` characters matching column widths.
- Subsequent rows: one transaction per line.
- Date column: left-aligned; width = max(len(formatted_date), len(label)).
- Beneficiary column (optional — only when source statement has a "Beneficiário" column): left-aligned; width = max(len(beneficiary), len(label)); inserted between Date and Description (FR-014).
- Description column: left-aligned; width = max(len(description), len(label)).
- Amount column: right-aligned; width = max(len(formatted_amount), len(label)).
- Columns separated by two spaces.
- Negative amounts prefixed with `-`; non-negative amounts prefixed with `+` (FR-008).
- Transaction dates from pt-BR long format (`14 de mar. 2026`) are normalised to the output locale's date format before display (FR-013).

---

## Standard Error (non-zero exit)

| Condition | stderr message | exit |
|-----------|---------------|------|
| No argument | `Usage: python -m credit_card_statement_extractor.transaction_extractor <file_path> [--lang <code>]` | 1 |
| File not found | `Error: File not found: <path>` | 1 |
| Not a valid PDF | `Error: Could not parse as PDF: <path>` | 2 |
| No transactions found | `Error: No transactions found in <path>` | 2 |
| Some lines skipped | `Warning: <N> line(s) could not be parsed and were skipped.` | 0 (continues) |
| Internal error | `Error: An unexpected error occurred. Please report this issue.` | 3 |

- Stdout is empty on all error exits (exit codes 1, 2, 3).
- Warning (partial parse) is emitted to stderr; parsed transactions are still printed to stdout.

---

## Invocation Examples

```bash
# Default (English output)
python -m credit_card_statement_extractor.transaction_extractor statement.pdf

# Brazilian Portuguese output
python -m credit_card_statement_extractor.transaction_extractor statement.pdf --lang pt-BR

# Explicit English
python -m credit_card_statement_extractor.transaction_extractor statement.pdf --lang en
```

---

## Stability

This contract is **v0.1.0** and subject to change without a major version bump until the project reaches v1.0.0. Breaking changes to this contract at v1.0+ require a major version increment and migration notes (per constitution Development Workflow).
