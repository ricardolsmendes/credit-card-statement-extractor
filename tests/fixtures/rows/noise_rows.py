# Raw rows that are NOT transactions and must be filtered out.

NOISE_ROWS: list[list[str]] = [
    # Blank rows
    ["", "", ""],
    ["   ", "  ", " "],
    # Total rows (EN)
    ["Total", "3 transactions", "1.234,56"],
    ["Subtotal", "", "5.000,00"],
    ["New Balance", "", "3.200,00"],
    ["Previous Balance", "", "1.500,00"],
    ["Minimum Payment", "", "150,00"],
    ["Interest Charge", "", "45,00"],
    # Total rows (PT)
    ["Saldo", "", "2.000,00"],
    ["Saldo Anterior", "", "1.800,00"],
    ["Total de encargos", "", "120,00"],
    ["Pagamento recebido", "obrigado", "-500,00"],
    ["Limite disponível", "", "10.000,00"],
    ["Vencimento", "15/03/2024", ""],
    ["Juros", "", "30,00"],
    ["Taxa", "Anuidade", "250,00"],
    ["Tarifa", "SMS", "9,90"],
    # Page marker
    ["Page 1 of 3", "", ""],
    # Sparse row (only 1 non-empty cell)
    ["Some text", "", ""],
]

# Header rows (should be classified as HEADER, not NOISE or TRANSACTION)
HEADER_ROWS: list[list[str]] = [
    ["Date", "Description", "Amount"],
    ["Data", "Descrição", "Valor"],
    ["Data", "Estabelecimento", "Valor (R$)"],
    ["DATE", "MERCHANT", "AMOUNT"],
    ["Data", "Histórico", "Valor"],
]
