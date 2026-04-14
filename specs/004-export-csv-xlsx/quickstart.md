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
python -m credit_card_statement_extractor.transaction_extractor statement.pdf --output-format csv
```

Output file created: `statement-transactions.csv` (same directory as the input PDF)

Expected stdout:
```
Exported 4 transactions to statement-transactions.csv
```

Generated `statement-transactions.csv`:
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
python -m credit_card_statement_extractor.transaction_extractor faturas.pdf --lang pt-BR --output-format csv
```

Output file created: `faturas-transactions.csv`

Expected stdout:
```
Exported 4 transactions to faturas-transactions.csv
```

Generated `faturas-transactions.csv`:
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
python -m credit_card_statement_extractor.transaction_extractor statement.pdf --output-format xlsx
```

Output file created: `statement-transactions.xlsx`

Expected stdout:
```
Exported 4 transactions to statement-transactions.xlsx
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
python -m credit_card_statement_extractor.transaction_extractor statement_with_beneficiary.pdf --lang pt-BR --output-format csv
```

Output file: `statement_with_beneficiary-transactions.csv`

```
Data,Beneficiário,Descrição,Valor
14/03/2026,DrinksEBar,DrinksEBar,-85.91
14/03/2026,PostoDeGasolina,ABASTEC*Posto,-169.66
```

---

## Default table output (unchanged)

Omitting `--output-format` still prints the table to stdout:

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

**xlsxwriter not installed**:
```bash
python -m credit_card_statement_extractor.transaction_extractor statement.pdf --output-format xlsx
# stderr: Error: XLSX export requires xlsxwriter. Install it with: pip install xlsxwriter
# exit:   1
```

**Write permission denied**:
```bash
python -m credit_card_statement_extractor.transaction_extractor /read-only/statement.pdf --output-format csv
# stderr: Error: Cannot write to output file: /read-only/statement-transactions.csv
# exit:   1
```

---

## Running tests

```bash
uv run pytest tests/unit/transaction_extractor/
uv run pytest tests/integration/transaction_extractor/
uv run pytest   # full suite
```
