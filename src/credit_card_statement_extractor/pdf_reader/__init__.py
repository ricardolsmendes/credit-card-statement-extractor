"""PDF reader sub-package.

To use a different PDF library, implement the ``PDFReader`` Protocol and
update the import in ``__main__.py``. No other files need to change.
"""

from credit_card_statement_extractor.pdf_reader._pdfplumber_reader import PdfplumberReader
from credit_card_statement_extractor.pdf_reader._protocol import PageResult, PDFReader

__all__ = ["PDFReader", "PageResult", "PdfplumberReader"]
