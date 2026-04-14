"""Locale configuration for transaction output formatting."""

import dataclasses


@dataclasses.dataclass(frozen=True)
class LocaleConfig:
    """Display configuration for a single output language/region.

    Attributes:
        code: Language tag (e.g. ``"en"``, ``"pt-BR"``).
        date_format: strftime format string for date display.
        decimal_separator: Character used as decimal separator.
        thousands_separator: Character used as thousands separator.
        currency_prefix: String prepended to formatted amounts (may be empty).
        col_date: Column header label for the Date column.
        col_description: Column header label for the Description column.
        col_amount: Column header label for the Amount column.
    """

    code: str
    date_format: str
    decimal_separator: str
    thousands_separator: str
    currency_prefix: str
    col_date: str
    col_description: str
    col_amount: str
    col_beneficiary: str


#: English locale — ISO 8601 dates, period decimal, no currency prefix.
LOCALE_EN = LocaleConfig(
    code="en",
    date_format="%Y-%m-%d",
    decimal_separator=".",
    thousands_separator=",",
    currency_prefix="",
    col_date="Date",
    col_description="Description",
    col_amount="Amount",
    col_beneficiary="Beneficiary",
)

#: Brazilian Portuguese locale — added in T017 (US2).
#: Placeholder reference; the actual constant is defined below for completeness
#: but exported from here once T017 runs.  Import it only after T017 completes.
LOCALE_PT_BR = LocaleConfig(
    code="pt-BR",
    date_format="%d/%m/%Y",
    decimal_separator=",",
    thousands_separator=".",
    currency_prefix="R$ ",
    col_date="Data",
    col_description="Descrição",
    col_amount="Valor",
    col_beneficiary="Beneficiário",
)
