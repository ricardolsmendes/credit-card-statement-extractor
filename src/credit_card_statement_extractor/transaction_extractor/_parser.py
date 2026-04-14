"""DefaultParser — extracts transactions from pdfplumber page text."""

import datetime
import decimal
import re

from credit_card_statement_extractor.pdf_reader._protocol import PageResult
from credit_card_statement_extractor.transaction_extractor._models import Transaction

# ---------------------------------------------------------------------------
# Header keywords
# ---------------------------------------------------------------------------

_DATE_HEADERS = frozenset(
    {
        "date",
        "data",
        "data da compra",
        "data lancamento",
        "data lançamento",
    }
)

_DESCRIPTION_HEADERS = frozenset(
    {
        "description",
        "descricao",
        "descrição",
        "historico",
        "histórico",
        "movimentacao",
        "movimentação",
        "estabelecimento",
    }
)

_AMOUNT_HEADERS = frozenset(
    {
        "amount",
        "valor",
        "valor (r$)",
    }
)

# Beneficiary header — distinct from description headers (FR-014)
_BENEFICIARY_HEADERS = frozenset(
    {
        "beneficiario",
        "beneficiário",
    }
)


# ---------------------------------------------------------------------------
# Transaction line regex
# ---------------------------------------------------------------------------
# Pattern:
#   group 1 — date:        long pt-BR format ("14 de mar. 2026") OR numeric
#   group 2 — description: any non-empty text (lazy)
#   group 3 — amount:      optional sign, optional currency prefix, digit, then digits/separators
#
_TXN_RE = re.compile(
    r"^(\d{1,2} de \w+\.?\s+\d{4}|\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|\d{4}[/\-]\d{1,2}[/\-]\d{1,2})"
    r"\s+"
    r"(.+?)"
    r"\s+"
    r"([+\-]?\s*(?:R\$\s*)?\d[\d.,]*)$"
)

# Date formats tried in order (after long-format check)
_DATE_FORMATS = [
    "%d/%m/%Y",
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%d/%m/%y",
    "%Y/%m/%d",
]

# pt-BR month abbreviation → month number (FR-013)
_PT_BR_MONTHS: dict[str, int] = {
    "jan": 1,
    "fev": 2,
    "mar": 3,
    "abr": 4,
    "mai": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "set": 9,
    "out": 10,
    "nov": 11,
    "dez": 12,
}


def _parse_date(raw: str) -> datetime.date:
    """Try multiple date formats; raise ValueError if none match.

    Long pt-BR format ("14 de mar. 2026") is attempted first.
    """
    # Try long pt-BR format first: "DD de MMM[.] YYYY"
    if " de " in raw:
        parts = raw.split()
        # Expected tokens: ["14", "de", "mar.", "2026"] or ["14", "de", "mar", "2026"]
        if len(parts) == 4 and parts[1].lower() == "de":
            try:
                day = int(parts[0])
                month_token = parts[2].rstrip(".").lower()
                year = int(parts[3])
                month = _PT_BR_MONTHS.get(month_token)
                if month is None:
                    raise ValueError(f"Unknown month abbreviation: {month_token!r}")
                return datetime.date(year, month, day)
            except (ValueError, IndexError):
                raise ValueError(f"Cannot parse long pt-BR date: {raw!r}")

    for fmt in _DATE_FORMATS:
        try:
            return datetime.datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {raw!r}")


def _normalise_amount(raw: str) -> decimal.Decimal:
    """Normalise a raw amount string to a Decimal.

    Handles optional leading currency prefix (e.g. "- R$ 85,91" → Decimal('-85.91')).

    Heuristic: if the string contains both '.' and ',' determine which is
    the decimal separator by position (last separator before final 1–2 digits).
    If only one separator present with 3 digits after, it's a thousands sep.
    """
    # Strip leading sign for analysis
    sign = ""
    s = raw.strip()
    if s.startswith(("+", "-")):
        sign = s[0]
        s = s[1:].strip()

    # Strip optional currency prefix: "R$ " or "$ "
    s = re.sub(r"^R?\$\s*", "", s).strip()

    if "," in s and "." in s:
        # Both present: determine which is decimal by position of last separator
        last_comma = s.rfind(",")
        last_dot = s.rfind(".")
        if last_comma > last_dot:
            # comma is decimal (pt-BR style): 1.234,56
            s = s.replace(".", "").replace(",", ".")
        else:
            # dot is decimal (en style): 1,234.56
            s = s.replace(",", "")
    elif "," in s:
        # Only comma — check if it could be thousands or decimal
        after_comma = s[s.rfind(",") + 1 :]
        if len(after_comma) == 3:
            # Thousands separator: 1,234
            s = s.replace(",", "")
        else:
            # Decimal separator: 4,50
            s = s.replace(",", ".")
    # else: only dots or nothing — leave as-is

    if sign == "-":
        return decimal.Decimal(f"-{s}")
    return decimal.Decimal(s)


def _is_header_line(line: str) -> bool:
    """Return True if the line contains recognisable date/description/amount headers."""
    tokens = {t.strip().lower() for t in re.split(r"\s{2,}|\t", line) if t.strip()}
    # Also split on single spaces for simple headers like "Date Description Amount"
    single_tokens = {t.strip().lower() for t in line.split() if t.strip()}
    all_tokens = tokens | single_tokens

    has_date = bool(all_tokens & _DATE_HEADERS)
    has_amount = bool(all_tokens & _AMOUNT_HEADERS)

    # At least date + amount (description and beneficiary headers may vary)
    return has_date and has_amount


def _find_beneficiary_col_index(line: str) -> int | None:
    """Return the column index of the beneficiary header token in ``line``.

    Tries multi-space split first (≥2 spaces, for raw text with preserved spacing),
    then single-space split (for pdfplumber-extracted text where spacing was collapsed).
    Returns None if no beneficiary header token is found.

    The returned index is always relative to the *single-space* token list so that
    it aligns with the single-space token positions in transaction rows extracted
    from the same source.
    """
    single_tokens = [t.strip().lower() for t in line.split() if t.strip()]
    for i, token in enumerate(single_tokens):
        if token in _BENEFICIARY_HEADERS:
            return i
    return None


class DefaultParser:
    """Parse transactions from pdfplumber page text.

    Scans all pages for a recognised transaction table header, then extracts
    transaction rows using a regex.  Returns transactions in source order plus
    a count of lines that could not be parsed after the header was found.

    Raises:
        ValueError: If no recognised transaction table header is found.
    """

    def parse(self, pages: list[PageResult]) -> tuple[list[Transaction], int]:
        """Extract transactions from ``pages``.

        Returns:
            A tuple of (transactions, skipped_count) where skipped_count is
            the number of lines after the header that looked like data rows
            but could not be parsed as transactions.
        """
        transactions: list[Transaction] = []
        skipped = 0
        header_found = False
        beneficiary_col_index: int | None = None  # position in single-space token list

        for page in pages:
            lines = page.text.splitlines()
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue

                if not header_found:
                    if _is_header_line(stripped):
                        header_found = True
                        beneficiary_col_index = _find_beneficiary_col_index(stripped)
                    continue

                # After header: try to parse as transaction
                m = _TXN_RE.match(stripped)
                if m:
                    date_str, desc, amount_str = m.groups()
                    try:
                        date = _parse_date(date_str)
                        amount = _normalise_amount(amount_str)

                        # Extract beneficiary from token at recorded column position.
                        # The header column index is based on single-space tokens of the
                        # header line, where "Data" is 1 token.  In a long-date row,
                        # "14 de mar. 2026" occupies 4 tokens, creating an offset of 3.
                        # We adjust by counting how many single-space tokens the actual
                        # date string consumes minus 1 (since the header "Data" = 1 token).
                        beneficiary: str | None = None
                        description = desc.strip()
                        if beneficiary_col_index is not None:
                            date_token_count = len(date_str.split())
                            # header has 1 token for the date label; row has date_token_count
                            date_offset = date_token_count - 1
                            adjusted_index = beneficiary_col_index + date_offset
                            row_tokens = stripped.split()
                            if adjusted_index < len(row_tokens):
                                beneficiary = row_tokens[adjusted_index]
                                # Reconstruct description from tokens between date and
                                # beneficiary (excluding the beneficiary token itself).
                                desc_tokens = row_tokens[date_token_count:adjusted_index]
                                description = " ".join(desc_tokens)
                            else:
                                beneficiary = ""

                        transactions.append(
                            Transaction(
                                date=date,
                                description=description,
                                amount=amount,
                                beneficiary=beneficiary,
                            )
                        )
                    except (ValueError, decimal.InvalidOperation):
                        skipped += 1
                else:
                    # Non-empty, non-transaction line after header.
                    # Count it as skipped (malformed / unrecognised data row).
                    skipped += 1

        if not header_found:
            raise ValueError("No transaction table header found in the provided pages.")

        return transactions, skipped
