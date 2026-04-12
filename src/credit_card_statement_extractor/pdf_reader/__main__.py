"""CLI entry point: python -m credit_card_statement_extractor.pdf_reader <file_path>"""

import sys
from pathlib import Path

# To swap the PDF library: replace PdfplumberReader with your own implementation
# of the PDFReader protocol. No other changes are required.
from credit_card_statement_extractor.pdf_reader._pdfplumber_reader import PdfplumberReader


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: python -m credit_card_statement_extractor.pdf_reader <file_path>",
            file=sys.stderr,
        )
        sys.exit(1)

    path = Path(sys.argv[1])
    reader = PdfplumberReader()

    try:
        pages = reader.read(path)
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except ValueError:
        print(f"Error: Could not parse as PDF: {path}", file=sys.stderr)
        sys.exit(2)

    for page in pages:
        print(f"--- Page {page.page_number} ---")
        print(page.text)


if __name__ == "__main__":
    main()
