import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

# Ordered list of date format patterns — DD/MM/YYYY first (PT-BR default)
_DATE_FORMATS: list[str] = [
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%d/%m/%y",
    "%m/%d/%y",
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%d %b %Y",
    "%d %b %y",
    "%b %d, %Y",
    "%b %d %Y",
]

# Currency prefix/symbols to strip before numeric parsing
_CURRENCY_RE = re.compile(r"R\$|[\$€£]")
# Parentheses wrapping: (value) means negative
_PARENS_RE = re.compile(r"^\((.+)\)$")


def parse_date(raw: str) -> date | None:
    """
    Try each date format in priority order; return the first successful parse or None.
    DD/MM/YYYY is tried before MM/DD/YYYY to favour PT-BR statements by default.
    """
    stripped = raw.strip()
    if not stripped:
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(stripped, fmt).date()
        except ValueError:
            continue
    return None


def parse_amount(raw: str) -> Decimal | None:
    """
    Normalize raw amount strings into Decimal.

    Handles:
    - Currency prefixes: "R$ 1.234,56" -> Decimal("1234.56")
    - Parentheses negative (PT-BR accounting): "(1.234,56)" -> Decimal("-1234.56")
    - EN format: "1,234.56" -> Decimal("1234.56")
    - PT-BR format: "1.234,56" -> Decimal("1234.56")
    - Plain negative: "-1234.56"
    - Integers: "150"

    Disambiguation rule:
    - If both '.' and ',' present: whichever appears last is the decimal separator.
    - If only one type present: if it precedes exactly 3 trailing digits it's a
      thousands separator (no decimal part); otherwise it's the decimal separator.
    """
    stripped = raw.strip()
    if not stripped:
        return None

    # Strip currency symbols
    stripped = _CURRENCY_RE.sub("", stripped).strip()

    # Check for parentheses-as-negative and unwrap
    negative = False
    parens_match = _PARENS_RE.match(stripped)
    if parens_match:
        negative = True
        stripped = parens_match.group(1).strip()
    elif stripped.startswith("-"):
        negative = True
        stripped = stripped[1:].strip()

    # Strip any remaining whitespace or stray currency chars
    stripped = _CURRENCY_RE.sub("", stripped).strip()

    if not stripped:
        return None

    # Find positions of all dots and commas
    dot_positions = [i for i, c in enumerate(stripped) if c == "."]
    comma_positions = [i for i, c in enumerate(stripped) if c == ","]

    try:
        if dot_positions and comma_positions:
            # Both present: last one is decimal separator
            last_dot = dot_positions[-1]
            last_comma = comma_positions[-1]
            if last_comma > last_dot:
                # Comma is decimal: PT-BR "1.234,56"
                normalized = stripped.replace(".", "").replace(",", ".")
            else:
                # Dot is decimal: EN "1,234.56"
                normalized = stripped.replace(",", "")
        elif dot_positions:
            # Only dots present
            digits_after = len(stripped) - dot_positions[-1] - 1
            if digits_after == 3 and len(dot_positions) == 1:
                # Thousands separator, no decimal: "1.234"
                normalized = stripped.replace(".", "")
            else:
                # Decimal separator: "1234.56"
                normalized = stripped.replace(",", "")  # strip any comma artefacts
        elif comma_positions:
            # Only commas present
            digits_after = len(stripped) - comma_positions[-1] - 1
            if digits_after == 3 and len(comma_positions) == 1:
                # Thousands separator, no decimal: "1,234"
                normalized = stripped.replace(",", "")
            else:
                # Decimal separator: "1234,56"
                normalized = stripped.replace(",", ".")
        else:
            normalized = stripped

        result = Decimal(normalized)
    except InvalidOperation:
        return None

    return -result if negative else result


def normalize_description(raw: str) -> str:
    """Collapse multiple whitespace, strip leading/trailing whitespace."""
    return " ".join(raw.split())
