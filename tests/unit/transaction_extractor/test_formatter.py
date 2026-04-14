"""Unit tests for Formatter (T007, T016, T037)."""

import datetime
import decimal

import pytest

from credit_card_statement_extractor.transaction_extractor._formatter import Formatter
from credit_card_statement_extractor.transaction_extractor._locale import (
    LOCALE_EN,
    LOCALE_PT_BR,
)
from credit_card_statement_extractor.transaction_extractor._models import Transaction

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def en_transactions() -> list[Transaction]:
    return [
        Transaction(
            date=datetime.date(2026, 3, 1),
            description="Coffee Shop",
            amount=decimal.Decimal("-4.50"),
        ),
        Transaction(
            date=datetime.date(2026, 3, 2),
            description="Grocery Store",
            amount=decimal.Decimal("-82.10"),
        ),
        Transaction(
            date=datetime.date(2026, 3, 10),
            description="Payment received",
            amount=decimal.Decimal("500.00"),
        ),
        Transaction(
            date=datetime.date(2026, 3, 15),
            description="Gas Station",
            amount=decimal.Decimal("-89.50"),
        ),
    ]


# ---------------------------------------------------------------------------
# T007: English locale tests
# ---------------------------------------------------------------------------


class TestFormatterEnglish:
    def test_header_contains_date_description_amount(
        self, en_transactions: list[Transaction]
    ) -> None:
        result = Formatter().render(en_transactions, LOCALE_EN)
        lines = result.split("\n")
        assert "Date" in lines[0]
        assert "Description" in lines[0]
        assert "Amount" in lines[0]

    def test_separator_line_exists(self, en_transactions: list[Transaction]) -> None:
        result = Formatter().render(en_transactions, LOCALE_EN)
        lines = result.split("\n")
        assert lines[1].startswith("--")

    def test_separator_length_matches_header(self, en_transactions: list[Transaction]) -> None:
        result = Formatter().render(en_transactions, LOCALE_EN)
        lines = result.split("\n")
        header_len = len(lines[0])
        sep_len = len(lines[1])
        assert sep_len == header_len

    def test_four_transaction_rows(self, en_transactions: list[Transaction]) -> None:
        result = Formatter().render(en_transactions, LOCALE_EN)
        lines = [ln for ln in result.split("\n") if ln.strip()]
        # header + separator + 4 transactions = 6 non-empty lines
        assert len(lines) == 6

    def test_date_formatted_yyyy_mm_dd(self, en_transactions: list[Transaction]) -> None:
        result = Formatter().render(en_transactions, LOCALE_EN)
        assert "2026-03-01" in result

    def test_negative_amount_prefixed_minus(self, en_transactions: list[Transaction]) -> None:
        result = Formatter().render(en_transactions, LOCALE_EN)
        assert "-4.50" in result

    def test_positive_amount_prefixed_plus(self, en_transactions: list[Transaction]) -> None:
        result = Formatter().render(en_transactions, LOCALE_EN)
        assert "+500.00" in result

    def test_column_widths_accommodate_longest_value(
        self, en_transactions: list[Transaction]
    ) -> None:
        result = Formatter().render(en_transactions, LOCALE_EN)
        lines = result.split("\n")
        # All data rows should have the same length as the header (fixed-width)
        header_len = len(lines[0])
        for line in lines[2:]:
            if line.strip():
                assert len(line) == header_len


# ---------------------------------------------------------------------------
# T016: pt-BR locale tests
# ---------------------------------------------------------------------------


class TestFormatterPtBr:
    def test_header_contains_ptbr_labels(self, en_transactions: list[Transaction]) -> None:
        result = Formatter().render(en_transactions, LOCALE_PT_BR)
        lines = result.split("\n")
        assert "Data" in lines[0]
        assert "Descrição" in lines[0]
        assert "Valor" in lines[0]

    def test_date_formatted_dd_mm_yyyy(self, en_transactions: list[Transaction]) -> None:
        result = Formatter().render(en_transactions, LOCALE_PT_BR)
        assert "01/03/2026" in result

    def test_amount_uses_comma_decimal(self, en_transactions: list[Transaction]) -> None:
        result = Formatter().render(en_transactions, LOCALE_PT_BR)
        # -4.50 → -R$ 4,50
        assert "4,50" in result

    def test_amount_uses_r_prefix(self, en_transactions: list[Transaction]) -> None:
        result = Formatter().render(en_transactions, LOCALE_PT_BR)
        assert "R$" in result

    def test_negative_amount_prefix(self, en_transactions: list[Transaction]) -> None:
        result = Formatter().render(en_transactions, LOCALE_PT_BR)
        # Negative amounts: -R$ 4,50
        assert "-R$" in result

    def test_positive_amount_prefix(self, en_transactions: list[Transaction]) -> None:
        result = Formatter().render(en_transactions, LOCALE_PT_BR)
        # Positive amounts: +R$ 500,00
        assert "+R$" in result


# ---------------------------------------------------------------------------
# T037: has_beneficiary parameter tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def beneficiary_transactions() -> list[Transaction]:
    return [
        Transaction(
            date=datetime.date(2026, 3, 14),
            description="DrinksEBar",
            amount=decimal.Decimal("-85.91"),
            beneficiary="DrinksEBar",
        ),
        Transaction(
            date=datetime.date(2026, 3, 14),
            description="ABASTEC*Posto",
            amount=decimal.Decimal("-169.66"),
            beneficiary="PostoDeGasolina",
        ),
    ]


class TestFormatterBeneficiaryColumn:
    def test_beneficiary_header_in_ptbr_output(
        self, beneficiary_transactions: list[Transaction]
    ) -> None:
        result = Formatter().render(beneficiary_transactions, LOCALE_PT_BR, has_beneficiary=True)
        assert "Benefici" in result.split("\n")[0]  # matches "Beneficiário"

    def test_beneficiary_header_in_en_output(
        self, beneficiary_transactions: list[Transaction]
    ) -> None:
        result = Formatter().render(beneficiary_transactions, LOCALE_EN, has_beneficiary=True)
        assert "Beneficiary" in result.split("\n")[0]

    def test_beneficiary_column_between_date_and_description(
        self, beneficiary_transactions: list[Transaction]
    ) -> None:
        result = Formatter().render(beneficiary_transactions, LOCALE_PT_BR, has_beneficiary=True)
        header = result.split("\n")[0]
        date_pos = header.index("Data")
        beneficiary_pos = header.index("Benefici")
        desc_pos = header.index("Descri")
        assert date_pos < beneficiary_pos < desc_pos

    def test_beneficiary_column_absent_when_false(self, en_transactions: list[Transaction]) -> None:
        result = Formatter().render(en_transactions, LOCALE_EN, has_beneficiary=False)
        assert "Beneficiary" not in result
        assert "Benefici" not in result

    def test_beneficiary_column_absent_by_default(self, en_transactions: list[Transaction]) -> None:
        result = Formatter().render(en_transactions, LOCALE_EN)
        assert "Beneficiary" not in result

    def test_beneficiary_values_appear_in_rows(
        self, beneficiary_transactions: list[Transaction]
    ) -> None:
        result = Formatter().render(beneficiary_transactions, LOCALE_PT_BR, has_beneficiary=True)
        assert "DrinksEBar" in result
        assert "PostoDeGasolina" in result

    def test_beneficiary_column_left_aligned(
        self, beneficiary_transactions: list[Transaction]
    ) -> None:
        result = Formatter().render(beneficiary_transactions, LOCALE_EN, has_beneficiary=True)
        lines = result.split("\n")
        # All non-empty rows should have the same length as header (fixed-width)
        header_len = len(lines[0])
        for line in lines[2:]:
            if line.strip():
                assert len(line) == header_len
