# Quickstart: Transaction Extractor

**Feature**: 003-extract-transactions

---

## Prerequisites

Feature 002 (`pdf_reader`) must be installed:

```bash
uv sync --all-extras
```

---

## Extract transactions (English output)

```bash
python -m credit_card_statement_extractor.transaction_extractor statement.pdf
```

Expected output:

```
Date        Description                    Amount
----------  -----------------------------  -----------
2026-03-01  Coffee Shop                         -4.50
2026-03-02  Grocery Store                      -82.10
2026-03-10  Payment received                  +500.00
2026-03-15  Gas Station                        -89.50
```

---

## Extract transactions (Brazilian Portuguese output)

```bash
python -m credit_card_statement_extractor.transaction_extractor statement.pdf --lang pt-BR
```

Expected output:

```
Data        Descrição                      Valor
----------  -----------------------------  -----------
01/03/2026  Coffee Shop                     -R$ 4,50
02/03/2026  Supermercado ABC               -R$ 82,10
10/03/2026  Pagamento recebido            +R$ 500,00
15/03/2026  Posto de Gasolina              -R$ 89,50
```

---

## Error scenarios

**File not found**:

```bash
python -m credit_card_statement_extractor.transaction_extractor missing.pdf
# stderr: Error: File not found: missing.pdf
# exit:   1
```

**Not a valid PDF**:

```bash
python -m credit_card_statement_extractor.transaction_extractor notes.txt
# stderr: Error: Could not parse as PDF: notes.txt
# exit:   2
```

**No transactions found**:

```bash
python -m credit_card_statement_extractor.transaction_extractor blank.pdf
# stderr: Error: No transactions found in blank.pdf
# exit:   2
```

**Partial parse (some lines skipped)**:

```bash
python -m credit_card_statement_extractor.transaction_extractor messy.pdf
# stderr: Warning: 3 line(s) could not be parsed and were skipped.
# stdout: <table with successfully parsed transactions>
# exit:   0
```

---

## Running tests

```bash
uv run pytest tests/unit/transaction_extractor/
uv run pytest tests/integration/transaction_extractor/
uv run pytest   # full suite
```
