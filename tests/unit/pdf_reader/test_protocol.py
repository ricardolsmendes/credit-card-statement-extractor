"""Unit tests for PageResult dataclass and PDFReader Protocol."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from credit_card_statement_extractor.pdf_reader._protocol import PageResult, PDFReader


class TestPageResult:
    def test_construction_valid(self):
        result = PageResult(page_number=1, text="Hello")
        assert result.page_number == 1
        assert result.text == "Hello"

    def test_construction_empty_text_is_allowed(self):
        result = PageResult(page_number=1, text="")
        assert result.text == ""

    def test_page_number_zero_raises(self):
        with pytest.raises(ValueError, match="page_number"):
            PageResult(page_number=0, text="text")

    def test_page_number_negative_raises(self):
        with pytest.raises(ValueError, match="page_number"):
            PageResult(page_number=-1, text="text")

    def test_is_frozen(self):
        result = PageResult(page_number=1, text="hello")
        with pytest.raises(FrozenInstanceError):
            result.text = "other"  # type: ignore[misc]


class TestPDFReaderProtocol:
    def test_null_reader_satisfies_protocol(self):
        """A class with read(Path) -> list[PageResult] is structurally compatible."""

        class NullReader:
            def read(self, path: Path) -> list[PageResult]:
                return []

        assert isinstance(NullReader(), PDFReader)

    def test_class_without_read_does_not_satisfy_protocol(self):
        class NotAReader:
            pass

        assert not isinstance(NotAReader(), PDFReader)
