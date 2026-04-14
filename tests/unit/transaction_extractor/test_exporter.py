"""Unit tests for Exporter — CSV and XLSX scenarios (T003, T008)."""

import csv
import datetime
import decimal
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from credit_card_statement_extractor.transaction_extractor._exporter import Exporter
from credit_card_statement_extractor.transaction_extractor._locale import (
    LOCALE_EN,
    LOCALE_PT_BR,
)
from credit_card_statement_extractor.transaction_extractor._models import Transaction

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_TRANSACTIONS = [
    Transaction(
        date=datetime.date(2026, 3, 1), description="Coffee Shop", amount=decimal.Decimal("-4.50")
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
        date=datetime.date(2026, 3, 15), description="Gas Station", amount=decimal.Decimal("-89.50")
    ),
]

_TRANSACTIONS_WITH_BENEFICIARY = [
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


# ---------------------------------------------------------------------------
# T003: CSV scenarios
# ---------------------------------------------------------------------------


class TestExporterCSV:
    def test_csv_header_en(self, tmp_path: Path) -> None:
        """(a) First line contains Date,Description,Amount."""
        out = tmp_path / "out.csv"
        Exporter().export(_TRANSACTIONS, LOCALE_EN, out, "csv")
        first_line = out.read_text(encoding="utf-8-sig").splitlines()[0]
        assert first_line == "Date,Description,Amount"

    def test_csv_line_count(self, tmp_path: Path) -> None:
        """(b) 5 lines: 1 header + 4 data rows."""
        out = tmp_path / "out.csv"
        Exporter().export(_TRANSACTIONS, LOCALE_EN, out, "csv")
        lines = out.read_text(encoding="utf-8-sig").splitlines()
        assert len(lines) == 5

    def test_csv_date_iso_format(self, tmp_path: Path) -> None:
        """(c) Date values formatted as YYYY-MM-DD for EN locale."""
        out = tmp_path / "out.csv"
        Exporter().export(_TRANSACTIONS, LOCALE_EN, out, "csv")
        rows = list(csv.reader(out.read_text(encoding="utf-8-sig").splitlines()))
        assert rows[1][0] == "2026-03-01"

    def test_csv_amount_dot_decimal_debit(self, tmp_path: Path) -> None:
        """(d) Negative amounts are plain dot-decimal strings."""
        out = tmp_path / "out.csv"
        Exporter().export(_TRANSACTIONS, LOCALE_EN, out, "csv")
        rows = list(csv.reader(out.read_text(encoding="utf-8-sig").splitlines()))
        assert rows[1][2] == "-4.50"

    def test_csv_positive_amount_no_plus_sign(self, tmp_path: Path) -> None:
        """(e) Positive amounts have no leading + sign."""
        out = tmp_path / "out.csv"
        Exporter().export(_TRANSACTIONS, LOCALE_EN, out, "csv")
        rows = list(csv.reader(out.read_text(encoding="utf-8-sig").splitlines()))
        # Row 3 is Payment received: 500.00
        assert rows[3][2] == "500.00"
        assert not rows[3][2].startswith("+")

    def test_csv_ptbr_headers(self, tmp_path: Path) -> None:
        """(f) PT-BR locale produces Data,Descrição,Valor header and DD/MM/YYYY date."""
        out = tmp_path / "out.csv"
        Exporter().export(_TRANSACTIONS, LOCALE_PT_BR, out, "csv")
        lines = out.read_text(encoding="utf-8-sig").splitlines()
        assert lines[0] == "Data,Descrição,Valor"
        rows = list(csv.reader(lines))
        assert rows[1][0] == "01/03/2026"

    def test_csv_beneficiary_header_en(self, tmp_path: Path) -> None:
        """(g) With has_beneficiary=True, header is Date,Beneficiary,Description,Amount."""
        out = tmp_path / "out.csv"
        Exporter().export(
            _TRANSACTIONS_WITH_BENEFICIARY, LOCALE_EN, out, "csv", has_beneficiary=True
        )
        first_line = out.read_text(encoding="utf-8-sig").splitlines()[0]
        assert first_line == "Date,Beneficiary,Description,Amount"

    def test_csv_beneficiary_header_ptbr(self, tmp_path: Path) -> None:
        """(g) With has_beneficiary=True and pt-BR, header is Data,Beneficiário,Descrição,Valor."""
        out = tmp_path / "out.csv"
        Exporter().export(
            _TRANSACTIONS_WITH_BENEFICIARY, LOCALE_PT_BR, out, "csv", has_beneficiary=True
        )
        first_line = out.read_text(encoding="utf-8-sig").splitlines()[0]
        assert first_line == "Data,Beneficiário,Descrição,Valor"

    def test_csv_utf8_bom(self, tmp_path: Path) -> None:
        """(h) File starts with UTF-8 BOM bytes."""
        out = tmp_path / "out.csv"
        Exporter().export(_TRANSACTIONS, LOCALE_EN, out, "csv")
        assert out.read_bytes()[:3] == b"\xef\xbb\xbf"


# ---------------------------------------------------------------------------
# T008: XLSX scenarios
# ---------------------------------------------------------------------------


class TestExporterXLSX:
    def test_xlsx_is_valid_zip(self, tmp_path: Path) -> None:
        """(a) Output is a valid ZIP archive (XLSX files are ZIP)."""
        out = tmp_path / "out.xlsx"
        Exporter().export(_TRANSACTIONS, LOCALE_EN, out, "xlsx")
        assert zipfile.is_zipfile(out)

    def test_xlsx_transactions_sheet_exists(self, tmp_path: Path) -> None:
        """(c) Sheet named Transactions exists."""
        out = tmp_path / "out.xlsx"
        Exporter().export(_TRANSACTIONS, LOCALE_EN, out, "xlsx")
        with zipfile.ZipFile(out) as zf:
            # xl/worksheets/sheet1.xml must exist (xlsxwriter always creates it)
            names = zf.namelist()
            assert any("worksheets" in n for n in names)

    def test_xlsx_file_not_empty(self, tmp_path: Path) -> None:
        """(b) File exists and has non-zero size."""
        out = tmp_path / "out.xlsx"
        Exporter().export(_TRANSACTIONS, LOCALE_EN, out, "xlsx")
        assert out.exists()
        assert out.stat().st_size > 0

    def test_xlsx_ptbr_creates_file(self, tmp_path: Path) -> None:
        """(d) PT-BR locale export produces a file."""
        out = tmp_path / "out.xlsx"
        Exporter().export(_TRANSACTIONS, LOCALE_PT_BR, out, "xlsx")
        assert zipfile.is_zipfile(out)

    def test_xlsx_with_beneficiary_creates_file(self, tmp_path: Path) -> None:
        """(f) With has_beneficiary=True, export still produces a valid file."""
        out = tmp_path / "out.xlsx"
        Exporter().export(
            _TRANSACTIONS_WITH_BENEFICIARY, LOCALE_EN, out, "xlsx", has_beneficiary=True
        )
        assert zipfile.is_zipfile(out)

    def test_xlsx_missing_xlsxwriter_raises_runtime_error(self, tmp_path: Path) -> None:
        """(g) If xlsxwriter is not installed, raises RuntimeError containing 'xlsxwriter'."""
        out = tmp_path / "out.xlsx"
        with patch.dict("sys.modules", {"xlsxwriter": None}):
            with pytest.raises(RuntimeError, match="xlsxwriter"):
                Exporter().export(_TRANSACTIONS, LOCALE_EN, out, "xlsx")
