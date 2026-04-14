"""Formatter — renders a list of Transactions as a fixed-width table."""

import decimal

from credit_card_statement_extractor.transaction_extractor._locale import LocaleConfig
from credit_card_statement_extractor.transaction_extractor._models import Transaction

_MIN_DATE_WIDTH = 10
_MIN_DESC_WIDTH = 20
_MIN_AMOUNT_WIDTH = 12
_MIN_BENEFICIARY_WIDTH = 12
_COL_SEP = "  "


def _format_amount(amount: decimal.Decimal, locale: LocaleConfig) -> str:
    """Format ``amount`` using locale separators and currency prefix."""
    sign = "+" if amount >= 0 else "-"
    abs_val = abs(amount)

    # Format absolute value with 2 decimal places
    int_part, _, frac_part = f"{abs_val:.2f}".partition(".")

    # Apply thousands separator
    # Group int_part into chunks of 3 from the right
    groups: list[str] = []
    s = int_part
    while len(s) > 3:
        groups.append(s[-3:])
        s = s[:-3]
    groups.append(s)
    formatted_int = locale.thousands_separator.join(reversed(groups))

    formatted = f"{formatted_int}{locale.decimal_separator}{frac_part}"
    return f"{sign}{locale.currency_prefix}{formatted}"


class Formatter:
    """Render a list of ``Transaction`` objects as a fixed-width table.

    Usage::

        table = Formatter().render(transactions, LOCALE_EN)
        print(table)
    """

    def render(
        self,
        transactions: list[Transaction],
        locale: LocaleConfig,
        has_beneficiary: bool = False,
    ) -> str:
        """Produce a fixed-width table string.

        Column layout:
        - Date:         left-aligned, min width 10
        - Beneficiary:  left-aligned, min width 12 (only when has_beneficiary=True)
        - Description:  left-aligned, min width 20
        - Amount:       right-aligned, min width 12

        Columns separated by two spaces.  Header row, separator line, then
        one row per transaction.
        """
        # Pre-format values so we can compute column widths
        formatted_dates = [t.date.strftime(locale.date_format) for t in transactions]
        formatted_beneficiaries = [t.beneficiary or "" for t in transactions]
        formatted_descs = [t.description for t in transactions]
        formatted_amounts = [_format_amount(t.amount, locale) for t in transactions]

        # Compute column widths
        date_w = max(
            _MIN_DATE_WIDTH,
            len(locale.col_date),
            *(len(d) for d in formatted_dates) if formatted_dates else [0],
        )
        beneficiary_w = max(
            _MIN_BENEFICIARY_WIDTH,
            len(locale.col_beneficiary),
            *(len(b) for b in formatted_beneficiaries) if formatted_beneficiaries else [0],
        )
        desc_w = max(
            _MIN_DESC_WIDTH,
            len(locale.col_description),
            *(len(d) for d in formatted_descs) if formatted_descs else [0],
        )
        amount_w = max(
            _MIN_AMOUNT_WIDTH,
            len(locale.col_amount),
            *(len(a) for a in formatted_amounts) if formatted_amounts else [0],
        )

        # Build header
        if has_beneficiary:
            header = (
                locale.col_date.ljust(date_w)
                + _COL_SEP
                + locale.col_beneficiary.ljust(beneficiary_w)
                + _COL_SEP
                + locale.col_description.ljust(desc_w)
                + _COL_SEP
                + locale.col_amount.rjust(amount_w)
            )
        else:
            header = (
                locale.col_date.ljust(date_w)
                + _COL_SEP
                + locale.col_description.ljust(desc_w)
                + _COL_SEP
                + locale.col_amount.rjust(amount_w)
            )
        separator = "-" * len(header)

        # Build data rows
        rows: list[str] = [header, separator]
        for date_str, ben_str, desc_str, amount_str in zip(
            formatted_dates, formatted_beneficiaries, formatted_descs, formatted_amounts
        ):
            if has_beneficiary:
                row = (
                    date_str.ljust(date_w)
                    + _COL_SEP
                    + ben_str.ljust(beneficiary_w)
                    + _COL_SEP
                    + desc_str.ljust(desc_w)
                    + _COL_SEP
                    + amount_str.rjust(amount_w)
                )
            else:
                row = (
                    date_str.ljust(date_w)
                    + _COL_SEP
                    + desc_str.ljust(desc_w)
                    + _COL_SEP
                    + amount_str.rjust(amount_w)
                )
            rows.append(row)

        return "\n".join(rows)
