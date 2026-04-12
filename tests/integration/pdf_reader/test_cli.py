"""Integration tests for the pdf_reader CLI entry point."""

import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).parent.parent.parent / "fixtures" / "pdfs"
SINGLE_PAGE = FIXTURES / "single_page.pdf"
MULTI_PAGE = FIXTURES / "multi_page.pdf"
NOT_A_PDF = FIXTURES / "not_a_pdf.txt"
MODULE = "credit_card_statement_extractor.pdf_reader"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", MODULE, *args],
        capture_output=True,
        text=True,
    )


class TestCLISuccess:
    def test_single_page_exit_zero(self):
        result = run(str(SINGLE_PAGE))
        assert result.returncode == 0

    def test_single_page_contains_header(self):
        result = run(str(SINGLE_PAGE))
        assert "--- Page 1 ---" in result.stdout

    def test_single_page_stdout_non_empty(self):
        result = run(str(SINGLE_PAGE))
        assert result.stdout.strip() != ""

    def test_multi_page_exit_zero(self):
        result = run(str(MULTI_PAGE))
        assert result.returncode == 0

    def test_multi_page_has_both_headers(self):
        result = run(str(MULTI_PAGE))
        assert "--- Page 1 ---" in result.stdout
        assert "--- Page 2 ---" in result.stdout

    def test_no_stderr_on_success(self):
        result = run(str(SINGLE_PAGE))
        assert result.stderr == ""


class TestCLIErrors:
    def test_no_argument_exit_one(self):
        result = run()
        assert result.returncode == 1

    def test_no_argument_prints_usage_to_stderr(self):
        result = run()
        assert "Usage" in result.stderr or "usage" in result.stderr

    def test_no_argument_stdout_is_empty(self):
        result = run()
        assert result.stdout == ""

    def test_missing_file_exit_one(self):
        result = run("/nonexistent/path/file.pdf")
        assert result.returncode == 1

    def test_missing_file_message_on_stderr(self):
        result = run("/nonexistent/path/file.pdf")
        assert "not found" in result.stderr.lower() or "File not found" in result.stderr

    def test_missing_file_stdout_is_empty(self):
        result = run("/nonexistent/path/file.pdf")
        assert result.stdout == ""

    def test_non_pdf_exit_two(self):
        result = run(str(NOT_A_PDF))
        assert result.returncode == 2

    def test_non_pdf_message_on_stderr(self):
        result = run(str(NOT_A_PDF))
        assert "parse" in result.stderr.lower() or "PDF" in result.stderr

    def test_non_pdf_stdout_is_empty(self):
        result = run(str(NOT_A_PDF))
        assert result.stdout == ""
