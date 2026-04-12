"""PDF reader protocol and shared data types."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class PageResult:
    """Extracted text content for a single PDF page."""

    page_number: int
    text: str

    def __post_init__(self) -> None:
        if self.page_number < 1:
            raise ValueError(f"page_number must be >= 1, got {self.page_number}")


@runtime_checkable
class PDFReader(Protocol):
    """Swappable interface for PDF text extraction.

    To use a different PDF library, implement this Protocol and update
    the import in ``__main__.py``. No other files need to change.
    """

    def read(self, path: Path) -> list[PageResult]:
        """Extract text from every page of the PDF at ``path``.

        Args:
            path: Absolute or relative path to the PDF file.

        Returns:
            One ``PageResult`` per page, in document order, with
            1-based ``page_number`` values.

        Raises:
            FileNotFoundError: If ``path`` does not exist.
            ValueError: If the file cannot be parsed as a PDF.
        """
        ...
