import re
from enum import StrEnum

from credit_card_extractor.normalizer import parse_amount, parse_date

# Matches common date patterns before attempting full parse (fast pre-filter)
_DATE_PATTERN = re.compile(
    r"\b(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|\d{4}[/\-\.]\d{2}[/\-\.]\d{2})\b"
)

# Known noise phrases — matched case-insensitively at word boundaries
# These are all in lowercase for comparison
_NOISE_KEYWORDS: frozenset[str] = frozenset(
    [
        # English
        "total",
        "subtotal",
        "balance",
        "new balance",
        "previous balance",
        "payment",
        "minimum payment",
        "credit limit",
        "available credit",
        "statement balance",
        "interest charge",
        "annual fee",
        "page",
        "continued",
        "finance charge",
        # Portuguese
        "saldo",
        "saldo anterior",
        "saldo devedor",
        "pagamento",
        "pagamento recebido",
        "fatura",
        "limite",
        "limite disponível",
        "limite disponivel",
        "crédito disponível",
        "credito disponivel",
        "encargos",
        "juros",
        "taxa",
        "tarifa",
        "vencimento",
        "anuidade",
        "mínimo",
        "minimo",
        "mínimo a pagar",
        "minimo a pagar",
    ]
)

# Header keywords in both languages (case-insensitive)
_HEADER_KEYWORDS: frozenset[str] = frozenset(
    [
        # English
        "date",
        "description",
        "merchant",
        "amount",
        "reference",
        "category",
        "debit",
        "credit",
        "transaction",
        # Portuguese
        "data",
        "descrição",
        "descricao",
        "estabelecimento",
        "histórico",
        "historico",
        "valor",
        "referência",
        "referencia",
        "categoria",
        "débito",
        "debito",
        "crédito",
        "credito",
    ]
)


class RowClass(StrEnum):
    TRANSACTION = "transaction"
    HEADER = "header"
    NOISE = "noise"
    CONTINUATION = "continuation"


def _non_empty_cells(cells: list[str]) -> list[str]:
    return [c for c in cells if c and c.strip()]


def _cell_text(cell: str) -> str:
    return cell.strip().lower() if cell else ""


def _matches_noise_keyword(text: str) -> bool:
    """Return True if text exactly matches or starts with a noise keyword at a word boundary."""
    normalized = text.strip().lower()
    if normalized in _NOISE_KEYWORDS:
        return True
    for kw in _NOISE_KEYWORDS:
        if re.match(rf"^{re.escape(kw)}\b", normalized):
            return True
    return False


def looks_like_date(cell: str) -> bool:
    """Return True if cell matches a date pattern."""
    return bool(_DATE_PATTERN.search(cell.strip()))


def looks_like_amount(cell: str) -> bool:
    """Return True if cell can be parsed as a monetary amount."""
    return parse_amount(cell) is not None


def is_noise_row(cells: list[str]) -> bool:
    """
    Return True if this row should be discarded.

    Noise conditions (any of):
    1. Row is entirely blank.
    2. Fewer than 2 non-empty cells.
    3. Any cell matches a noise keyword.
    4. All cells are the same non-empty value (repeated header artifact).
    """
    non_empty = _non_empty_cells(cells)

    # Condition 1 & 2: blank or sparse
    if len(non_empty) < 2:
        return True

    # Condition 3: noise keyword in any cell
    for cell in non_empty:
        if _matches_noise_keyword(cell):
            return True

    # Condition 4: all cells identical
    if len(set(c.strip().lower() for c in non_empty)) == 1:
        return True

    return False


def is_header_row(cells: list[str]) -> bool:
    """
    Return True if this row looks like a column header row.
    A header row has no parseable dates and no parseable amounts,
    but contains at least one known header keyword.
    """
    non_empty = _non_empty_cells(cells)
    if not non_empty:
        return False

    # Must not contain any parseable dates or amounts
    for cell in non_empty:
        if looks_like_date(cell) and parse_date(cell) is not None:
            return False
        if looks_like_amount(cell):
            return False

    # Must contain at least one header keyword
    for cell in non_empty:
        normalized = _cell_text(cell)
        if normalized in _HEADER_KEYWORDS:
            return True
        # Allow header cells with extra characters like "Valor (R$)"
        for kw in _HEADER_KEYWORDS:
            if normalized.startswith(kw):
                return True

    return False


def infer_column_indices(header_row: list[str]) -> dict[str, int]:
    """
    Given a header row, return a mapping of semantic column name to 0-based index.

    Semantic names: "date", "description", "amount"
    Optional: "reference", "category"

    Falls back to positional guessing if headers are not recognized:
      col 0 = date, last col = amount, middle = description.
    """
    date_keywords = {"date", "data"}
    desc_keywords = {
        "description",
        "merchant",
        "descrição",
        "descricao",
        "estabelecimento",
        "histórico",
        "historico",
    }
    amount_keywords = {"amount", "valor", "debit", "débito", "debito"}
    reference_keywords = {"reference", "referência", "referencia"}
    category_keywords = {"category", "categoria"}

    result: dict[str, int] = {}

    for i, cell in enumerate(header_row):
        normalized = _cell_text(cell)
        if not normalized:
            continue

        if "date" not in result:
            if normalized in date_keywords or any(normalized.startswith(k) for k in date_keywords):
                result["date"] = i

        if "description" not in result:
            if normalized in desc_keywords or any(normalized.startswith(k) for k in desc_keywords):
                result["description"] = i

        if "amount" not in result:
            if normalized in amount_keywords or any(normalized.startswith(k) for k in amount_keywords):
                result["amount"] = i

        if "reference" not in result:
            if normalized in reference_keywords:
                result["reference"] = i

        if "category" not in result:
            if normalized in category_keywords:
                result["category"] = i

    # Positional fallback for unrecognized headers
    if len(header_row) >= 2:
        if "date" not in result:
            result["date"] = 0
        if "amount" not in result:
            result["amount"] = len(header_row) - 1
        if "description" not in result:
            # Middle column(s): pick the one not already claimed by date/amount
            taken = set(result.values())
            for i in range(len(header_row)):
                if i not in taken:
                    result["description"] = i
                    break

    return result


def classify_row(cells: list[str], col_indices: dict[str, int] | None = None) -> RowClass:
    """
    Classify a row as TRANSACTION, HEADER, NOISE, or CONTINUATION.

    col_indices: mapping from infer_column_indices(); if None, positional fallback is used.
    """
    if is_header_row(cells):
        return RowClass.HEADER

    # Determine which cells to treat as date, description, amount
    if col_indices and len(cells) > max(col_indices.values(), default=0):
        date_cell = cells[col_indices.get("date", 0)]
        amount_col = col_indices.get("amount", len(cells) - 1)
        amount_cell = cells[amount_col] if amount_col < len(cells) else ""
        desc_col = col_indices.get("description", 1 if len(cells) > 2 else 0)
        desc_cell = cells[desc_col] if desc_col < len(cells) else ""
    else:
        date_cell = cells[0] if cells else ""
        amount_cell = cells[-1] if len(cells) > 1 else ""
        desc_cell = cells[1] if len(cells) > 2 else (cells[1] if len(cells) == 2 else "")

    has_date = looks_like_date(date_cell) and parse_date(date_cell) is not None
    has_amount = looks_like_amount(amount_cell)
    has_description = bool(desc_cell and desc_cell.strip())

    if has_date and has_amount:
        return RowClass.TRANSACTION

    # No date, no amount, but has description text → continuation of previous transaction.
    # Check this BEFORE is_noise_row because continuation rows are intentionally sparse
    # (only one non-empty cell).
    if not has_date and not has_amount and has_description:
        # Make sure it's not a noise keyword before calling it a continuation
        if not _matches_noise_keyword(desc_cell):
            return RowClass.CONTINUATION

    if is_noise_row(cells):
        return RowClass.NOISE

    return RowClass.NOISE
