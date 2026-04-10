from datetime import date
from decimal import Decimal

import pytest

from credit_card_extractor.normalizer import normalize_description, parse_amount, parse_date


class TestParseDate:
    def test_ddmmyyyy(self):
        assert parse_date("15/03/2024") == date(2024, 3, 15)

    def test_ddmmyy(self):
        assert parse_date("15/03/24") == date(2024, 3, 15)

    def test_iso(self):
        assert parse_date("2024-03-15") == date(2024, 3, 15)

    def test_named_month_en(self):
        assert parse_date("15 Mar 2024") == date(2024, 3, 15)

    def test_named_month_short_year(self):
        assert parse_date("15 Mar 24") == date(2024, 3, 15)

    def test_us_format(self):
        # MM/DD/YYYY when day > 12 forces correct parse
        assert parse_date("03/15/2024") == date(2024, 3, 15)

    def test_ddmmyyyy_priority_over_mmddyyyy(self):
        # "01/02/2024" is ambiguous; DD/MM/YYYY has priority => Feb 1
        assert parse_date("01/02/2024") == date(2024, 2, 1)

    def test_invalid_returns_none(self):
        assert parse_date("not a date") is None

    def test_empty_returns_none(self):
        assert parse_date("") is None

    def test_whitespace_stripped(self):
        assert parse_date("  15/03/2024  ") == date(2024, 3, 15)


class TestParseAmount:
    def test_plain_decimal_en(self):
        assert parse_amount("125.40") == Decimal("125.40")

    def test_plain_decimal_ptbr(self):
        assert parse_amount("125,40") == Decimal("125.40")

    def test_thousands_en(self):
        assert parse_amount("1,234.56") == Decimal("1234.56")

    def test_thousands_ptbr(self):
        assert parse_amount("1.234,56") == Decimal("1234.56")

    def test_currency_symbol_r(self):
        assert parse_amount("R$ 1.234,56") == Decimal("1234.56")

    def test_currency_symbol_dollar(self):
        assert parse_amount("$ 1,234.56") == Decimal("1234.56")

    def test_plain_negative(self):
        assert parse_amount("-125.40") == Decimal("-125.40")

    def test_ptbr_negative_plain(self):
        assert parse_amount("-125,40") == Decimal("-125.40")

    def test_parens_negative(self):
        assert parse_amount("(125,40)") == Decimal("-125.40")

    def test_parens_negative_with_currency(self):
        assert parse_amount("(R$ 1.234,56)") == Decimal("-1234.56")

    def test_integer(self):
        assert parse_amount("150") == Decimal("150")

    def test_thousands_only_no_decimal(self):
        # "1.234" with exactly 3 digits after dot => thousands, result is 1234
        assert parse_amount("1.234") == Decimal("1234")

    def test_thousands_only_comma_no_decimal(self):
        assert parse_amount("1,234") == Decimal("1234")

    def test_empty_returns_none(self):
        assert parse_amount("") is None

    def test_whitespace_only_returns_none(self):
        assert parse_amount("   ") is None

    def test_non_numeric_returns_none(self):
        assert parse_amount("n/a") is None

    def test_large_amount(self):
        assert parse_amount("R$ 12.345,67") == Decimal("12345.67")


class TestNormalizeDescription:
    def test_strips_edges(self):
        assert normalize_description("  ABC  ") == "ABC"

    def test_collapses_internal_spaces(self):
        assert normalize_description("ABC   DEF") == "ABC DEF"

    def test_collapses_tabs_and_newlines(self):
        assert normalize_description("ABC\t\nDEF") == "ABC DEF"

    def test_empty_string(self):
        assert normalize_description("") == ""

    def test_preserves_single_space(self):
        assert normalize_description("ABC DEF") == "ABC DEF"
