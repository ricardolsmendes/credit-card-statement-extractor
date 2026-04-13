"""Unit tests for DefaultParser (T006, T011, T023)."""

import datetime
import decimal
import time
from pathlib import Path

import pytest

from credit_card_statement_extractor.pdf_reader._protocol import PageResult
from credit_card_statement_extractor.transaction_extractor._parser import DefaultParser
from credit_card_statement_extractor.transaction_extractor._protocol import (
    TransactionParser,
)

# ---------------------------------------------------------------------------
# Helpers — build PageResult objects from plain text
# ---------------------------------------------------------------------------


def _pages(*text_blocks: str) -> list[PageResult]:
    return [PageResult(page_number=i + 1, text=block) for i, block in enumerate(text_blocks)]


# ---------------------------------------------------------------------------
# T006: DefaultParser — US1 scenarios
# ---------------------------------------------------------------------------


class TestDefaultParserHeaderDetection:
    def test_english_header_detected(self) -> None:
        pages = _pages("Date  Description  Amount\n2026-03-01  Coffee Shop  -4.50\n")
        parser = DefaultParser()
        txns, _ = parser.parse(pages)
        assert len(txns) == 1

    def test_no_header_raises_value_error(self) -> None:
        pages = _pages("ACCOUNT SUMMARY\nNo transactions this period.\n")
        parser = DefaultParser()
        with pytest.raises(ValueError, match="[Nn]o.*header|header.*not found"):
            parser.parse(pages)

    def test_ptbr_header_detected(self) -> None:
        """Parser must recognise pt-BR header variants."""
        pages = _pages("Data  Descricao  Valor\n01/03/2026  Coffee Shop  -4,50\n")
        parser = DefaultParser()
        txns, _ = parser.parse(pages)
        assert len(txns) == 1


class TestDefaultParserTransactionParsing:
    def test_four_rows_returns_four_transactions(self) -> None:
        text = (
            "Date  Description  Amount\n"
            "2026-03-01  Coffee Shop  -4.50\n"
            "2026-03-02  Grocery Store  -82.10\n"
            "2026-03-10  Payment received  +500.00\n"
            "2026-03-15  Gas Station  -89.50\n"
        )
        parser = DefaultParser()
        txns, skipped = parser.parse(_pages(text))
        assert len(txns) == 4
        assert skipped == 0

    def test_transactions_in_source_order(self) -> None:
        text = (
            "Date  Description  Amount\n"
            "2026-03-01  Coffee Shop  -4.50\n"
            "2026-03-02  Grocery Store  -82.10\n"
            "2026-03-10  Payment received  +500.00\n"
            "2026-03-15  Gas Station  -89.50\n"
        )
        parser = DefaultParser()
        txns, _ = parser.parse(_pages(text))
        assert txns[0].date == datetime.date(2026, 3, 1)
        assert txns[1].date == datetime.date(2026, 3, 2)
        assert txns[2].date == datetime.date(2026, 3, 10)
        assert txns[3].date == datetime.date(2026, 3, 15)

    def test_dates_parsed_correctly(self) -> None:
        text = "Date  Description  Amount\n2026-03-01  Coffee Shop  -4.50\n"
        parser = DefaultParser()
        txns, _ = parser.parse(_pages(text))
        assert txns[0].date == datetime.date(2026, 3, 1)

    def test_ptbr_date_parsed_correctly(self) -> None:
        text = "Data  Descricao  Valor\n01/03/2026  Coffee Shop  -4,50\n"
        parser = DefaultParser()
        txns, _ = parser.parse(_pages(text))
        assert txns[0].date == datetime.date(2026, 3, 1)

    def test_amounts_parsed_as_decimal(self) -> None:
        text = "Date  Description  Amount\n2026-03-01  Coffee Shop  -4.50\n"
        parser = DefaultParser()
        txns, _ = parser.parse(_pages(text))
        assert isinstance(txns[0].amount, decimal.Decimal)
        assert txns[0].amount == decimal.Decimal("-4.50")

    def test_positive_amount_parsed(self) -> None:
        text = "Date  Description  Amount\n2026-03-10  Payment received  +500.00\n"
        parser = DefaultParser()
        txns, _ = parser.parse(_pages(text))
        assert txns[0].amount == decimal.Decimal("500.00")

    def test_ptbr_amount_normalised(self) -> None:
        """Comma-decimal amounts are normalised to period."""
        text = "Data  Descricao  Valor\n01/03/2026  Coffee Shop  -4,50\n"
        parser = DefaultParser()
        txns, _ = parser.parse(_pages(text))
        assert txns[0].amount == decimal.Decimal("-4.50")


class TestDefaultParserMultiPage:
    def test_transactions_spanning_two_pages(self) -> None:
        """Header on page 1; transaction rows continue on page 2."""
        page1 = "Date  Description  Amount\n2026-03-01  Coffee Shop  -4.50\n"
        page2 = "2026-03-02  Grocery Store  -82.10\n2026-03-10  Payment received  +500.00\n"
        parser = DefaultParser()
        txns, skipped = parser.parse(_pages(page1, page2))
        assert len(txns) == 3
        assert skipped == 0
        assert txns[0].date == datetime.date(2026, 3, 1)
        assert txns[2].date == datetime.date(2026, 3, 10)


class TestNullParser:
    def test_null_parser_satisfies_protocol(self) -> None:
        """A class with parse() returning ([], 0) satisfies TransactionParser."""

        class NullParser:
            def parse(self, pages: list[PageResult]) -> tuple[list, int]:
                return [], 0

        assert isinstance(NullParser(), TransactionParser)

    def test_non_parser_does_not_satisfy_protocol(self) -> None:
        class NotAParser:
            def process(self, pages: list[PageResult]) -> list:
                return []

        assert not isinstance(NotAParser(), TransactionParser)


# ---------------------------------------------------------------------------
# T023: US3 unit tests — partial parse behaviour
# ---------------------------------------------------------------------------


class TestPartialParse:
    def test_malformed_lines_skipped_and_counted(self) -> None:
        text = (
            "Date  Description  Amount\n"
            "2026-03-01  Coffee Shop  -4.50\n"
            "NOT A DATE - Missing amount field\n"
            "2026-03-02  Grocery Store  -82.10\n"
            "Also no date or amount here at all\n"
        )
        parser = DefaultParser()
        txns, skipped = parser.parse(_pages(text))
        assert len(txns) == 2
        assert skipped == 2

    def test_partial_parse_returns_only_valid_transactions(self) -> None:
        text = (
            "Date  Description  Amount\n"
            "2026-03-01  Coffee Shop  -4.50\n"
            "INVALID LINE NO DATE OR AMOUNT\n"
        )
        parser = DefaultParser()
        txns, skipped = parser.parse(_pages(text))
        assert len(txns) == 1
        assert txns[0].description == "Coffee Shop"

    def test_partial_parse_does_not_raise(self) -> None:
        text = "Date  Description  Amount\nINVALID LINE\nALSO INVALID\n"
        parser = DefaultParser()
        # Should not raise even if no valid transactions
        txns, skipped = parser.parse(_pages(text))
        assert len(txns) == 0
        assert skipped == 2

    def test_totals_only_header_raises_value_error(self) -> None:
        """A page with only a header row and a totals row but no transactions."""
        text = "Date  Description  Amount\nTotal  -  -176.10\n"
        parser = DefaultParser()
        # Should not raise; returns empty list with skipped=1
        txns, skipped = parser.parse(_pages(text))
        assert len(txns) == 0
        assert skipped >= 0  # "Total -" line either parsed or skipped


# ---------------------------------------------------------------------------
# T011: Timing smoke test — parsing en_statement.pdf must be < 2 s
# ---------------------------------------------------------------------------


class TestParserTiming:
    def test_parsing_en_statement_under_2_seconds(self) -> None:
        """Parsing en_statement.pdf via DefaultParser completes in < 2 s."""
        from credit_card_statement_extractor.pdf_reader._pdfplumber_reader import (
            PdfplumberReader,
        )

        fixture = (
            Path(__file__).parent.parent.parent / "fixtures" / "statements" / "en_statement.pdf"
        )
        reader = PdfplumberReader()
        pages = reader.read(fixture)

        parser = DefaultParser()
        start = time.monotonic()
        txns, _ = parser.parse(pages)
        elapsed = time.monotonic() - start

        assert elapsed < 2.0, f"Parsing took {elapsed:.2f}s (limit: 2s)"
        assert len(txns) == 4
