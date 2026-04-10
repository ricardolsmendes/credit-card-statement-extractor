# Raw rows that represent valid credit card transactions.
# Each row is [date_cell, description_cell, amount_cell].

VALID_TRANSACTIONS: list[list[str]] = [
    ["15/03/2024", "SUPERMERCADO ABC", "-125,40"],
    ["01/01/2024", "POSTO SHELL FILIAL 5", "R$ 80,00"],
    ["12/12/2023", "AMAZON.COM PAYMENTS", "1,234.56"],
    ["31/07/2024", "RESTAURANTE DO JOAO", "(50,00)"],
    ["15/03/2024", "COFFEE SHOP", "5.50"],
    ["22/11/2023", "UBER", "R$ 1.234,56"],
    ["03/08/2024", "NETFLIX", "-14.99"],
]

# Rows where the description continues on a second row (no date/amount)
CONTINUATION_ROWS: list[list[str]] = [
    ["", "MENOS FILIAL 03 CENTRO", ""],
    ["", "LTDA ME", ""],
    ["", "- LOJA 42", ""],
]
