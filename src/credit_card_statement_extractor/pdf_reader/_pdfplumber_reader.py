"""pdfplumber-backed implementation of the PDFReader protocol."""

from pathlib import Path

import pdfplumber

from credit_card_statement_extractor.pdf_reader._protocol import PageResult


class PdfplumberReader:
    """Extracts text from PDF files using ``pdfplumber``.

    To swap this for a different library, create a new class that provides
    ``read(path: Path) -> list[PageResult]`` and update the import in
    ``__main__.py``.  No other files need to change.
    """

    def read(self, path: Path) -> list[PageResult]:
        """Extract text page by page from the PDF at ``path``.

        Raises:
            FileNotFoundError: If ``path`` does not exist.
            ValueError: If the file cannot be parsed as a PDF.
        """
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            with pdfplumber.open(path) as pdf:
                return [
                    PageResult(page_number=i + 1, text=page.extract_text() or "")
                    for i, page in enumerate(pdf.pages)
                ]
        except FileNotFoundError:
            raise
        except Exception as exc:
            raise ValueError(f"Could not parse as PDF: {path}") from exc
