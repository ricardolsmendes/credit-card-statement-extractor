"""Integration tests for the transaction_extractor CLI (T013, T019, T022, T026)."""

import subprocess
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Fixture paths
# ---------------------------------------------------------------------------

FIXTURES = Path(__file__).parent.parent.parent / "fixtures" / "statements"
EN_PDF = FIXTURES / "en_statement.pdf"
PTBR_PDF = FIXTURES / "ptbr_statement.pdf"
NO_TXN_PDF = FIXTURES / "no_transactions_statement.pdf"
PARTIAL_PDF = FIXTURES / "partial_statement.pdf"
NOT_PDF = Path(__file__).parent.parent.parent / "fixtures" / "pdfs" / "not_a_pdf.txt"


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "credit_card_statement_extractor.transaction_extractor", *args],
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# T013: US1 — English extraction
# ---------------------------------------------------------------------------


class TestUS1English:
    def test_exit_0_on_valid_en_pdf(self) -> None:
        result = _run(str(EN_PDF))
        assert result.returncode == 0

    def test_stdout_contains_date_header(self) -> None:
        result = _run(str(EN_PDF))
        assert "Date" in result.stdout

    def test_stdout_contains_description_header(self) -> None:
        result = _run(str(EN_PDF))
        assert "Description" in result.stdout

    def test_stdout_contains_amount_header(self) -> None:
        result = _run(str(EN_PDF))
        assert "Amount" in result.stdout

    def test_stdout_contains_4_transaction_rows(self) -> None:
        result = _run(str(EN_PDF))
        lines = [ln for ln in result.stdout.strip().split("\n") if ln.strip()]
        # header + separator + 4 transactions = 6 lines
        assert len(lines) == 6

    def test_transactions_in_source_order(self) -> None:
        result = _run(str(EN_PDF))
        lines = result.stdout.strip().split("\n")
        data_lines = lines[2:]  # skip header + separator
        data_lines = [ln for ln in data_lines if ln.strip()]
        assert "2026-03-01" in data_lines[0]
        assert "2026-03-02" in data_lines[1]
        assert "2026-03-10" in data_lines[2]
        assert "2026-03-15" in data_lines[3]

    def test_negative_amount_starts_with_minus(self) -> None:
        result = _run(str(EN_PDF))
        assert "-4.50" in result.stdout

    def test_positive_amount_starts_with_plus(self) -> None:
        result = _run(str(EN_PDF))
        assert "+500.00" in result.stdout

    def test_stdout_empty_on_error(self) -> None:
        result = _run("nonexistent_file.pdf")
        assert result.returncode != 0
        assert result.stdout == ""


# ---------------------------------------------------------------------------
# T019: US2 — Language selection
# ---------------------------------------------------------------------------


class TestUS2Language:
    def test_lang_ptbr_exit_0(self) -> None:
        result = _run(str(EN_PDF), "--lang", "pt-BR")
        assert result.returncode == 0

    def test_lang_ptbr_headers(self) -> None:
        result = _run(str(EN_PDF), "--lang", "pt-BR")
        assert "Data" in result.stdout
        assert "Valor" in result.stdout

    def test_lang_ptbr_dates_dd_mm_yyyy(self) -> None:
        result = _run(str(EN_PDF), "--lang", "pt-BR")
        assert "01/03/2026" in result.stdout

    def test_lang_ptbr_amounts_with_r_dollar(self) -> None:
        result = _run(str(EN_PDF), "--lang", "pt-BR")
        assert "R$" in result.stdout

    def test_lang_ptbr_amounts_comma_decimal(self) -> None:
        result = _run(str(EN_PDF), "--lang", "pt-BR")
        assert "4,50" in result.stdout

    def test_lang_en_explicit_same_as_default(self) -> None:
        result_default = _run(str(EN_PDF))
        result_explicit = _run(str(EN_PDF), "--lang", "en")
        assert result_default.stdout == result_explicit.stdout

    def test_no_lang_defaults_to_english(self) -> None:
        result = _run(str(EN_PDF))
        assert "Date" in result.stdout
        assert "Description" in result.stdout
        assert "Amount" in result.stdout


# ---------------------------------------------------------------------------
# T022: US3 — Error handling
# ---------------------------------------------------------------------------


class TestUS3ErrorHandling:
    def test_no_argument_exit_1(self) -> None:
        result = _run()
        assert result.returncode == 1

    def test_no_argument_usage_on_stderr(self) -> None:
        result = _run()
        assert "Usage" in result.stderr or "usage" in result.stderr

    def test_missing_file_exit_1(self) -> None:
        result = _run("definitely_missing_file.pdf")
        assert result.returncode == 1

    def test_missing_file_message_on_stderr(self) -> None:
        result = _run("definitely_missing_file.pdf")
        assert "not found" in result.stderr.lower() or "File" in result.stderr

    def test_not_a_pdf_exit_2(self) -> None:
        result = _run(str(NOT_PDF))
        assert result.returncode == 2

    def test_not_a_pdf_message_on_stderr(self) -> None:
        result = _run(str(NOT_PDF))
        assert "parse" in result.stderr.lower() or "PDF" in result.stderr

    def test_no_transactions_exit_2(self) -> None:
        result = _run(str(NO_TXN_PDF))
        assert result.returncode == 2

    def test_no_transactions_message_on_stderr(self) -> None:
        result = _run(str(NO_TXN_PDF))
        assert "No transactions found" in result.stderr

    def test_partial_parse_exit_0(self) -> None:
        result = _run(str(PARTIAL_PDF))
        assert result.returncode == 0

    def test_partial_parse_warning_on_stderr(self) -> None:
        result = _run(str(PARTIAL_PDF))
        assert "Warning" in result.stderr
        assert "could not be parsed" in result.stderr

    def test_partial_parse_2_transaction_rows_on_stdout(self) -> None:
        result = _run(str(PARTIAL_PDF))
        lines = [ln for ln in result.stdout.strip().split("\n") if ln.strip()]
        # header + separator + 2 transactions = 4 lines
        assert len(lines) == 4

    def test_stdout_empty_on_exit_1(self) -> None:
        result = _run("missing.pdf")
        assert result.returncode == 1
        assert result.stdout == ""

    def test_stdout_empty_on_exit_2_no_transactions(self) -> None:
        result = _run(str(NO_TXN_PDF))
        assert result.returncode == 2
        assert result.stdout == ""


# ---------------------------------------------------------------------------
# T026: Timing smoke test — full CLI < 2 s
# ---------------------------------------------------------------------------


class TestCLITiming:
    def test_full_cli_completes_under_2_seconds(self) -> None:
        start = time.monotonic()
        result = _run(str(EN_PDF))
        elapsed = time.monotonic() - start
        assert result.returncode == 0
        assert elapsed < 2.0, f"CLI took {elapsed:.2f}s (limit: 2s)"
