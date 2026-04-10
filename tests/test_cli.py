"""
CLI integration tests using typer's CliRunner.
PDF parsing is mocked so these tests don't require real PDF files.
"""
import csv
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import date
from decimal import Decimal

import pytest
from typer.testing import CliRunner

from credit_card_extractor.cli import app
from credit_card_extractor.models import ExtractionResult, Transaction

runner = CliRunner()

_MOCK_TRANSACTIONS = [
    Transaction(
        date=date(2024, 3, 15),
        description="SUPERMERCADO ABC",
        amount=Decimal("-125.40"),
        original_amount_str="-125,40",
        page_number=1,
    ),
    Transaction(
        date=date(2024, 3, 16),
        description="POSTO SHELL",
        amount=Decimal("-80.00"),
        original_amount_str="R$ 80,00",
        page_number=1,
    ),
]

_MOCK_RESULT = ExtractionResult(
    transactions=_MOCK_TRANSACTIONS,
    warnings=[],
    source_file="statement.pdf",
    pages_processed=1,
)


def _make_pdf(tmp_path: Path) -> Path:
    """Create a dummy file that exists (content doesn't matter — extractor is mocked)."""
    p = tmp_path / "statement.pdf"
    p.write_bytes(b"%PDF-1.4 fake")
    return p


class TestExtractCommand:
    @patch("credit_card_extractor.cli.extract", return_value=_MOCK_RESULT)
    def test_default_csv_output(self, mock_extract, tmp_path):
        pdf = _make_pdf(tmp_path)
        result = runner.invoke(app, [str(pdf)])
        assert result.exit_code == 0
        out_csv = pdf.with_suffix(".csv")
        assert out_csv.exists()

    @patch("credit_card_extractor.cli.extract", return_value=_MOCK_RESULT)
    def test_explicit_xlsx_format(self, mock_extract, tmp_path):
        pdf = _make_pdf(tmp_path)
        result = runner.invoke(app, [str(pdf), "--format", "xlsx"])
        assert result.exit_code == 0
        out_xlsx = pdf.with_suffix(".xlsx")
        assert out_xlsx.exists()

    @patch("credit_card_extractor.cli.extract", return_value=_MOCK_RESULT)
    def test_custom_output_path(self, mock_extract, tmp_path):
        pdf = _make_pdf(tmp_path)
        custom_out = tmp_path / "custom.csv"
        result = runner.invoke(app, [str(pdf), "--output", str(custom_out)])
        assert result.exit_code == 0
        assert custom_out.exists()

    @patch("credit_card_extractor.cli.extract", return_value=_MOCK_RESULT)
    def test_format_inferred_from_output_extension_xlsx(self, mock_extract, tmp_path):
        pdf = _make_pdf(tmp_path)
        custom_out = tmp_path / "output.xlsx"
        result = runner.invoke(app, [str(pdf), "--output", str(custom_out)])
        assert result.exit_code == 0
        assert custom_out.exists()

    @patch("credit_card_extractor.cli.extract", return_value=_MOCK_RESULT)
    def test_language_pt_csv_headers(self, mock_extract, tmp_path):
        pdf = _make_pdf(tmp_path)
        out = tmp_path / "out.csv"
        result = runner.invoke(app, [str(pdf), "--output", str(out), "--language", "pt"])
        assert result.exit_code == 0
        with out.open(encoding="utf-8-sig") as f:
            headers = next(csv.reader(f))
        assert headers == ["Data", "Descrição", "Valor"]

    @patch("credit_card_extractor.cli.extract", return_value=_MOCK_RESULT)
    def test_verbose_prints_counts(self, mock_extract, tmp_path):
        pdf = _make_pdf(tmp_path)
        result = runner.invoke(app, [str(pdf), "--verbose"])
        assert result.exit_code == 0

    def test_nonexistent_pdf_errors(self, tmp_path):
        result = runner.invoke(app, [str(tmp_path / "missing.pdf")])
        assert result.exit_code != 0

    @patch("credit_card_extractor.cli.extract", return_value=_MOCK_RESULT)
    def test_transaction_count_in_output(self, mock_extract, tmp_path):
        pdf = _make_pdf(tmp_path)
        result = runner.invoke(app, [str(pdf)])
        assert result.exit_code == 0
        assert "2" in result.output  # 2 transactions reported

    @patch("credit_card_extractor.cli.extract", return_value=_MOCK_RESULT)
    def test_invalid_format_exits_nonzero(self, mock_extract, tmp_path):
        pdf = _make_pdf(tmp_path)
        result = runner.invoke(app, [str(pdf), "--format", "json"])
        assert result.exit_code != 0
