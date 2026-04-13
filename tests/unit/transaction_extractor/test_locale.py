"""Unit tests for LocaleConfig and locale constants (T006b, T015)."""

import datetime
import decimal

import pytest

from credit_card_statement_extractor.transaction_extractor._locale import (
    LOCALE_EN,
    LOCALE_PT_BR,
    LocaleConfig,
)


class TestLocaleConfigStructure:
    def test_is_frozen_dataclass(self) -> None:
        import dataclasses

        assert dataclasses.is_dataclass(LocaleConfig)

    def test_frozen_mutation_raises(self) -> None:
        import dataclasses

        with pytest.raises(dataclasses.FrozenInstanceError):
            LOCALE_EN.code = "xx"  # type: ignore[misc]


class TestLocaleEn:
    def test_code(self) -> None:
        assert LOCALE_EN.code == "en"

    def test_date_format(self) -> None:
        assert LOCALE_EN.date_format == "%Y-%m-%d"

    def test_decimal_separator(self) -> None:
        assert LOCALE_EN.decimal_separator == "."

    def test_thousands_separator(self) -> None:
        assert LOCALE_EN.thousands_separator == ","

    def test_currency_prefix_empty(self) -> None:
        assert LOCALE_EN.currency_prefix == ""

    def test_col_date(self) -> None:
        assert LOCALE_EN.col_date == "Date"

    def test_col_description(self) -> None:
        assert LOCALE_EN.col_description == "Description"

    def test_col_amount(self) -> None:
        assert LOCALE_EN.col_amount == "Amount"

    def test_positive_amount_formatting(self) -> None:
        """Positive amounts use +prefix and period decimal."""
        amount = decimal.Decimal("500.00")
        formatted = _format_amount(LOCALE_EN, amount)
        assert formatted.startswith("+")
        assert "." in formatted
        assert "500" in formatted

    def test_negative_amount_formatting(self) -> None:
        """Negative amounts use -prefix."""
        amount = decimal.Decimal("-4.50")
        formatted = _format_amount(LOCALE_EN, amount)
        assert formatted.startswith("-")
        assert "4" in formatted

    def test_date_formatting(self) -> None:
        """Dates use YYYY-MM-DD format."""
        d = datetime.date(2026, 3, 1)
        formatted = d.strftime(LOCALE_EN.date_format)
        assert formatted == "2026-03-01"


# ---------------------------------------------------------------------------
# T015: LOCALE_PT_BR tests
# ---------------------------------------------------------------------------


class TestLocalePtBr:
    def test_code(self) -> None:
        assert LOCALE_PT_BR.code == "pt-BR"

    def test_date_format(self) -> None:
        assert LOCALE_PT_BR.date_format == "%d/%m/%Y"

    def test_decimal_separator(self) -> None:
        assert LOCALE_PT_BR.decimal_separator == ","

    def test_thousands_separator(self) -> None:
        assert LOCALE_PT_BR.thousands_separator == "."

    def test_currency_prefix(self) -> None:
        assert LOCALE_PT_BR.currency_prefix == "R$ "

    def test_col_date(self) -> None:
        assert LOCALE_PT_BR.col_date == "Data"

    def test_col_description(self) -> None:
        assert LOCALE_PT_BR.col_description == "Descrição"

    def test_col_amount(self) -> None:
        assert LOCALE_PT_BR.col_amount == "Valor"

    def test_positive_amount_formatting(self) -> None:
        amount = decimal.Decimal("500.00")
        formatted = _format_amount(LOCALE_PT_BR, amount)
        assert formatted.startswith("+")
        assert "R$" in formatted
        assert "500,00" in formatted

    def test_negative_amount_formatting(self) -> None:
        amount = decimal.Decimal("-4.50")
        formatted = _format_amount(LOCALE_PT_BR, amount)
        assert formatted.startswith("-")
        assert "R$" in formatted
        assert "4,50" in formatted

    def test_date_formatting(self) -> None:
        d = datetime.date(2026, 3, 1)
        formatted = d.strftime(LOCALE_PT_BR.date_format)
        assert formatted == "01/03/2026"


# ---------------------------------------------------------------------------
# Helper — mirrors what Formatter.render() will do (tested more thoroughly
# in test_formatter.py; here we just verify locale config values drive output)
# ---------------------------------------------------------------------------


def _format_amount(locale: "LocaleConfig", amount: decimal.Decimal) -> str:
    sign = "+" if amount >= 0 else "-"
    abs_val = abs(amount)
    # Format with locale separators (simple: no thousands for test amounts)
    formatted = f"{abs_val:.2f}".replace(".", locale.decimal_separator)
    return f"{sign}{locale.currency_prefix}{formatted}"
