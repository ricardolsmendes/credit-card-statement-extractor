"""Unit tests for PdfplumberReader."""

import time
from pathlib import Path

import pytest

from credit_card_statement_extractor.pdf_reader._pdfplumber_reader import PdfplumberReader
from credit_card_statement_extractor.pdf_reader._protocol import PageResult

FIXTURES = Path(__file__).parent.parent.parent / "fixtures" / "pdfs"
SINGLE_PAGE = FIXTURES / "single_page.pdf"
MULTI_PAGE = FIXTURES / "multi_page.pdf"


class TestPdfplumberReader:
    def setup_method(self):
        self.reader = PdfplumberReader()

    def test_single_page_returns_one_result(self):
        pages = self.reader.read(SINGLE_PAGE)
        assert len(pages) == 1

    def test_single_page_result_is_page_result(self):
        pages = self.reader.read(SINGLE_PAGE)
        assert isinstance(pages[0], PageResult)

    def test_single_page_number_is_one(self):
        pages = self.reader.read(SINGLE_PAGE)
        assert pages[0].page_number == 1

    def test_single_page_text_is_non_empty(self):
        pages = self.reader.read(SINGLE_PAGE)
        assert pages[0].text.strip() != ""

    def test_multi_page_returns_two_results(self):
        pages = self.reader.read(MULTI_PAGE)
        assert len(pages) == 2

    def test_multi_page_numbers_are_sequential(self):
        pages = self.reader.read(MULTI_PAGE)
        assert pages[0].page_number == 1
        assert pages[1].page_number == 2

    def test_multi_page_text_non_empty(self):
        pages = self.reader.read(MULTI_PAGE)
        for page in pages:
            assert page.text.strip() != ""

    def test_missing_file_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            self.reader.read(Path("nonexistent.pdf"))

    def test_non_pdf_raises_value_error(self, tmp_path):
        bad = tmp_path / "bad.pdf"
        bad.write_text("not a pdf")
        with pytest.raises(ValueError):
            self.reader.read(bad)

    def test_timing_smoke_lower_bound(self):
        # lower-bound smoke test — SC-001 requires <5s for up to 50 pages;
        # validate against a real statement-sized PDF when fixtures are available.
        start = time.monotonic()
        self.reader.read(MULTI_PAGE)
        elapsed = time.monotonic() - start
        assert elapsed < 2.0, f"Extraction took {elapsed:.2f}s, expected < 2s"
