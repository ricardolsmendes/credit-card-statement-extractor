# CLI Contract: Export Transactions to CSV and XLSX

**Feature**: 004-export-csv-xlsx  
**Date**: 2026-04-14 (updated after clarification 2026-04-14)

---

## Updated CLI Interface

```
python -m credit_card_statement_extractor.transaction_extractor <file_path> [--lang <code>] [--output-format <format>]
```

### Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `file_path` | positional | yes | — | Path to the PDF statement |
| `--lang` | option | no | `en` | Output language: `en` or `pt-BR` |
| `--output-format` | option | no | — | Export format: `csv` or `xlsx` |

### Output file name derivation

When `--output-format` is given, the output file name is automatically derived:

```
<input_pdf_parent>/<input_pdf_stem>-transactions.<ext>
```

Examples:
- Input: `statement.pdf`, format `csv` → output: `statement-transactions.csv` (same dir)
- Input: `/data/jan_2026.pdf`, format `xlsx` → output: `/data/jan_2026-transactions.xlsx`
- Input: `./reports/march.pdf`, format `csv` → output: `./reports/march-transactions.csv`

---

## Behaviour by `--output-format` value

### `--output-format` omitted (existing behaviour — unchanged)

- Prints formatted table to stdout
- Warnings (skipped lines) to stderr
- Exit 0 on success

### `--output-format csv`

- Derives output path: `<input_stem>-transactions.csv` in same directory as input PDF
- Writes RFC 4180 CSV to the derived path
- UTF-8 with BOM encoding
- Columns: Date, [Beneficiary,] Description, Amount
- Column headers use the locale specified by `--lang`
- Date values: locale-formatted text string
- Amount values: plain numeric string with dot decimal, no currency symbol
- Prints confirmation to stdout: `Exported N transactions to <derived_path>`
- Does NOT print the table to stdout
- Exit 0 on success

### `--output-format xlsx`

- Derives output path: `<input_stem>-transactions.xlsx` in same directory as input PDF
- Writes valid XLSX file to the derived path
- Columns: same order as CSV
- Date values: native `datetime.date` cell type
- Amount values: native numeric cell type
- Prints confirmation to stdout: `Exported N transactions to <derived_path>`
- Does NOT print the table to stdout
- Exit 0 on success

---

## Error Cases

| Condition | stdout | stderr | Exit |
|-----------|--------|--------|------|
| Write permission denied on output directory | (empty) | `Error: Cannot write to output file: <path>` | 1 |
| `--output-format xlsx` but xlsxwriter not installed | (empty) | `Error: XLSX export requires xlsxwriter. Install it with: pip install xlsxwriter` | 1 |
| Zero transactions (existing path) | (empty) | `Error: No transactions found in <pdf>` | 2 |

*Note*: The `--output-format` argument is constrained by argparse `choices=["csv", "xlsx"]`, so invalid format values are rejected automatically with a usage error before reaching application logic.

---

## CSV File Format Contract

For input `statement.pdf --output-format csv`:

File: `statement-transactions.csv`

```
Date,Description,Amount
2026-03-01,Coffee Shop,-4.50
2026-03-02,Grocery Store,-82.10
2026-03-10,Payment received,500.00
2026-03-15,Gas Station,-89.50
```

With `--lang pt-BR`:

File: `statement-transactions.csv`

```
Data,Descrição,Valor
01/03/2026,Coffee Shop,-4.50
02/03/2026,Supermercado ABC,-82.10
10/03/2026,Pagamento recebido,500.00
15/03/2026,Posto de Gasolina,-89.50
```

With Beneficiário column present:

```
Data,Beneficiário,Descrição,Valor
14/03/2026,DrinksEBar,DrinksEBar,-85.91
14/03/2026,PostoDeGasolina,ABASTEC*Posto,-169.66
```

**Encoding**: UTF-8 with BOM  
**Line endings**: `\r\n` (RFC 4180)  
**Quoting**: Minimal — only quote fields containing commas, double-quotes, or newlines

---

## XLSX File Format Contract

- Sheet name: `Transactions`
- Row 1: Header row (bold)
- Row 2+: One row per transaction
- Date column: `datetime.date` type, display format `DD/MM/YYYY`
- Amount column: numeric type, display format `#,##0.00`
- All other columns: text type
