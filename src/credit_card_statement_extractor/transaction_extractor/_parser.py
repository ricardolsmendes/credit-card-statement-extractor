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


# ---------------------------------------------------------------------------
# Transaction line regex
# ---------------------------------------------------------------------------
# pdfplumber's extract_text() collapses multiple spaces to one, so we use
# \s+ (not \s{2,}) between description and amount.  The amount is the last
# whitespace-separated token that looks like a signed/unsigned number.
#
# Pattern:
#   group 1 — date:        1–2 digits, separator (/ or -), 1–2 digits, sep, 2–4 digits
#   group 2 — description: any non-empty text (lazy)
#   group 3 — amount:      optional sign, digit, then digits/separators
#
_TXN_RE = re.compile(
    r"^(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|\d{4}[/\-]\d{1,2}[/\-]\d{1,2})"
    r"\s+"
    r"(.+?)"
    r"\s+"
    r"([+\-]?\d[\d.,]*)$"
)

# Date formats tried in order
_DATE_FORMATS = [
    "%d/%m/%Y",
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%d/%m/%y",
    "%Y/%m/%d",
]


def _parse_date(raw: str) -> datetime.date:
    """Try multiple date formats; raise ValueError if none match."""
    for fmt in _DATE_FORMATS:
        try:
            return datetime.datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {raw!r}")


def _normalise_amount(raw: str) -> decimal.Decimal:
    """Normalise a raw amount string to a Decimal.

    Heuristic: if the string contains both '.' and ',' determine which is
    the decimal separator by position (last separator before final 1–2 digits).
    If only one separator present with 3 digits after, it's a thousands sep.
    """
    # Strip leading sign for analysis
    sign = ""
    s = raw
    if s.startswith(("+", "-")):
        sign = s[0]
        s = s[1:]

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

    # At least date + amount (description header may vary)
    return has_date and has_amount


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

        for page in pages:
            lines = page.text.splitlines()
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue

                if not header_found:
                    if _is_header_line(stripped):
                        header_found = True
                    continue

                # After header: try to parse as transaction
                m = _TXN_RE.match(stripped)
                if m:
                    date_str, desc, amount_str = m.groups()
                    try:
                        date = _parse_date(date_str)
                        amount = _normalise_amount(amount_str)
                        transactions.append(
                            Transaction(
                                date=date,
                                description=desc.strip(),
                                amount=amount,
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
