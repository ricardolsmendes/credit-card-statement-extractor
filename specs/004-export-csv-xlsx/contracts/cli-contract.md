# CLI Contract: Export Transactions to CSV and XLSX

**Feature**: 004-export-csv-xlsx  
**Date**: 2026-04-14

---

## Updated CLI Interface

```
python -m credit_card_statement_extractor.transaction_extractor <file_path> [--lang <code>] [--output <path>]
```

### Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `file_path` | positional | yes | — | Path to the PDF statement |
| `--lang` | option | no | `en` | Output language: `en` or `pt-BR` |
| `--output` | option | no | — | Output file path; `.csv` or `.xlsx` extension |

---

## Behaviour by `--output` value

### `--output` omitted (existing behaviour — unchanged)

- Prints formatted table to stdout
- Warnings (skipped lines) to stderr
- Exit 0 on success

### `--output transactions.csv`

- Writes RFC 4180 CSV to the specified path
- UTF-8 with BOM encoding
- Columns: Date, [Beneficiary,] Description, Amount
- Column headers use the locale specified by `--lang`
- Date values: locale-formatted text string
- Amount values: plain numeric string with dot decimal, no currency symbol
- Prints confirmation to stdout: `Exported N transactions to transactions.csv`
- Does NOT print the table to stdout
- Exit 0 on success

### `--output transactions.xlsx`

- Writes valid XLSX file to the specified path
- Columns: same order as CSV
- Date values: native `datetime.date` cell type
- Amount values: native numeric cell type
- Prints confirmation to stdout: `Exported N transactions to transactions.xlsx`
- Does NOT print the table to stdout
- Exit 0 on success

---

## Error Cases

| Condition | stdout | stderr | Exit |
|-----------|--------|--------|------|
| `--output` path has unrecognised extension | (empty) | `Error: Unsupported output format ".txt". Use .csv or .xlsx.` | 1 |
| `--output` parent directory does not exist | (empty) | `Error: Output directory does not exist: /path/to/dir` | 1 |
| Write permission denied | (empty) | `Error: Cannot write to output file: transactions.csv` | 1 |
| `--output file.xlsx` but xlsxwriter not installed | (empty) | `Error: XLSX export requires xlsxwriter. Install it with: pip install xlsxwriter` | 1 |
| Zero transactions (existing path) | (empty) | `Error: No transactions found in <pdf>` | 2 |

---

## CSV File Format Contract

```
Date,Description,Amount
2026-03-01,Coffee Shop,-4.50
2026-03-02,Grocery Store,-82.10
2026-03-10,Payment received,500.00
2026-03-15,Gas Station,-89.50
```

With `--lang pt-BR`:
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
- Date column: `datetime.date` type, display format `DD/MM/YYYY` (neutral, user can change in Excel)
- Amount column: numeric type, display format `#,##0.00`
- All other columns: text type
