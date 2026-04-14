# Quickstart: Export Transactions to CSV and XLSX

**Feature**: 004-export-csv-xlsx

---

## Prerequisites

Install the base package (CSV export works with no extras):

```bash
uv sync --all-extras
```

For XLSX export, install the `xlsx` extra:

```bash
uv sync --extra xlsx
# or: pip install xlsxwriter
```

---

## Export to CSV (English)

```bash
python -m credit_card_statement_extractor.transaction_extractor statement.pdf --output transactions.csv
```

Expected stdout:
```
Exported 4 transactions to transactions.csv
```

Generated `transactions.csv`:
```
Date,Description,Amount
2026-03-01,Coffee Shop,-4.50
2026-03-02,Grocery Store,-82.10
2026-03-10,Payment received,500.00
2026-03-15,Gas Station,-89.50
```

---

## Export to CSV (Brazilian Portuguese)

```bash
python -m credit_card_statement_extractor.transaction_extractor statement.pdf --lang pt-BR --output faturas.csv
```

Expected stdout:
```
Exported 4 transactions to faturas.csv
```

Generated `faturas.csv`:
```
Data,Descrição,Valor
01/03/2026,Coffee Shop,-4.50
02/03/2026,Supermercado ABC,-82.10
10/03/2026,Pagamento recebido,500.00
15/03/2026,Posto de Gasolina,-89.50
```

---

## Export to XLSX

```bash
python -m credit_card_statement_extractor.transaction_extractor statement.pdf --output transactions.xlsx
```

Expected stdout:
```
Exported 4 transactions to transactions.xlsx
```

The XLSX file contains:
- Sheet: `Transactions`
- Row 1: Bold headers — Date, Description, Amount
- Rows 2–5: One transaction per row
- Date column: native date type
- Amount column: native numeric type

---

## Export with Beneficiário column (pt-BR)

```bash
python -m credit_card_statement_extractor.transaction_extractor statement_with_beneficiary.pdf --lang pt-BR --output transactions.csv
```

Generated `transactions.csv`:
```
Data,Beneficiário,Descrição,Valor
14/03/2026,DrinksEBar,DrinksEBar,-85.91
14/03/2026,PostoDeGasolina,ABASTEC*Posto,-169.66
```

---

## Default table output (unchanged)

Omitting `--output` still prints the table to stdout:

```bash
python -m credit_card_statement_extractor.transaction_extractor statement.pdf
```

```
Date        Description                 Amount
----------------------------------------------
2026-03-01  Coffee Shop                  -4.50
...
```

---

## Error scenarios

**Unsupported extension**:
```bash
python -m credit_card_statement_extractor.transaction_extractor statement.pdf --output report.txt
# stderr: Error: Unsupported output format ".txt". Use .csv or .xlsx.
# exit:   1
```

**Output directory does not exist**:
```bash
python -m credit_card_statement_extractor.transaction_extractor statement.pdf --output /missing/dir/out.csv
# stderr: Error: Output directory does not exist: /missing/dir
# exit:   1
```

**xlsxwriter not installed**:
```bash
python -m credit_card_statement_extractor.transaction_extractor statement.pdf --output out.xlsx
# stderr: Error: XLSX export requires xlsxwriter. Install it with: pip install xlsxwriter
# exit:   1
```

---

## Running tests

```bash
uv run pytest tests/unit/transaction_extractor/
uv run pytest tests/integration/transaction_extractor/
uv run pytest   # full suite
```
