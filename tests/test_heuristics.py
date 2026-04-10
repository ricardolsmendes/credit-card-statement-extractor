import pytest

from credit_card_extractor.heuristics import (
    RowClass,
    classify_row,
    infer_column_indices,
    is_header_row,
    is_noise_row,
    looks_like_amount,
    looks_like_date,
)
from tests.fixtures.rows.noise_rows import HEADER_ROWS, NOISE_ROWS
from tests.fixtures.rows.transaction_rows import CONTINUATION_ROWS, VALID_TRANSACTIONS


class TestLooksLikeDate:
    def test_ddmmyyyy(self):
        assert looks_like_date("15/03/2024") is True

    def test_iso(self):
        assert looks_like_date("2024-03-15") is True

    def test_non_date(self):
        assert looks_like_date("SUPERMERCADO") is False

    def test_empty(self):
        assert looks_like_date("") is False


class TestLooksLikeAmount:
    def test_plain_decimal(self):
        assert looks_like_amount("125.40") is True

    def test_ptbr_format(self):
        assert looks_like_amount("1.234,56") is True

    def test_with_currency(self):
        assert looks_like_amount("R$ 80,00") is True

    def test_parens_negative(self):
        assert looks_like_amount("(50,00)") is True

    def test_non_amount(self):
        assert looks_like_amount("SUPERMERCADO") is False

    def test_empty(self):
        assert looks_like_amount("") is False


class TestIsNoiseRow:
    def test_blank_row(self):
        assert is_noise_row(["", "", ""]) is True

    def test_whitespace_only(self):
        assert is_noise_row(["   ", "  "]) is True

    @pytest.mark.parametrize("row", NOISE_ROWS)
    def test_noise_rows_from_fixtures(self, row):
        assert is_noise_row(row) is True

    @pytest.mark.parametrize("row", VALID_TRANSACTIONS)
    def test_valid_transactions_not_noise(self, row):
        assert is_noise_row(row) is False

    def test_total_keyword(self):
        assert is_noise_row(["Total", "charges", "1.500,00"]) is True

    def test_saldo_keyword(self):
        assert is_noise_row(["Saldo", "", "2.000,00"]) is True


class TestIsHeaderRow:
    @pytest.mark.parametrize("row", HEADER_ROWS)
    def test_header_rows_from_fixtures(self, row):
        assert is_header_row(row) is True

    @pytest.mark.parametrize("row", VALID_TRANSACTIONS)
    def test_valid_transactions_not_header(self, row):
        assert is_header_row(row) is False

    def test_english_headers(self):
        assert is_header_row(["Date", "Description", "Amount"]) is True

    def test_portuguese_headers(self):
        assert is_header_row(["Data", "Descrição", "Valor"]) is True

    def test_valor_with_extra(self):
        assert is_header_row(["Data", "Estabelecimento", "Valor (R$)"]) is True

    def test_blank_is_not_header(self):
        assert is_header_row(["", "", ""]) is False


class TestInferColumnIndices:
    def test_english_headers(self):
        indices = infer_column_indices(["Date", "Description", "Amount"])
        assert indices["date"] == 0
        assert indices["description"] == 1
        assert indices["amount"] == 2

    def test_portuguese_headers(self):
        indices = infer_column_indices(["Data", "Descrição", "Valor"])
        assert indices["date"] == 0
        assert indices["description"] == 1
        assert indices["amount"] == 2

    def test_positional_fallback_unrecognized(self):
        indices = infer_column_indices(["Col1", "Col2", "Col3"])
        assert indices["date"] == 0
        assert indices["amount"] == 2
        assert "description" in indices

    def test_optional_reference(self):
        indices = infer_column_indices(["Date", "Description", "Reference", "Amount"])
        assert indices.get("reference") == 2

    def test_optional_category(self):
        indices = infer_column_indices(["Date", "Merchant", "Category", "Amount"])
        assert indices.get("category") == 2


class TestClassifyRow:
    @pytest.mark.parametrize("row", VALID_TRANSACTIONS)
    def test_valid_transactions_classified_as_transaction(self, row):
        assert classify_row(row) == RowClass.TRANSACTION

    @pytest.mark.parametrize("row", CONTINUATION_ROWS)
    def test_continuation_rows_classified_correctly(self, row):
        assert classify_row(row) == RowClass.CONTINUATION

    @pytest.mark.parametrize("row", HEADER_ROWS)
    def test_header_rows_classified_as_header(self, row):
        assert classify_row(row) == RowClass.HEADER

    def test_noise_classified_as_noise(self):
        assert classify_row(["Total", "3 items", "1.500,00"]) == RowClass.NOISE

    def test_blank_classified_as_noise(self):
        assert classify_row(["", "", ""]) == RowClass.NOISE

    def test_uses_col_indices(self):
        # 4-column row: date at 0, desc at 1, ref at 2, amount at 3
        row = ["15/03/2024", "AMAZON", "REF123", "99.99"]
        indices = {"date": 0, "description": 1, "reference": 2, "amount": 3}
        assert classify_row(row, col_indices=indices) == RowClass.TRANSACTION
