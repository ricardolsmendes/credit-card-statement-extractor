"""Generate minimal valid PDF fixtures for testing.

Run once from the project root:
    python tests/fixtures/pdfs/create_fixtures.py
"""

import io
from pathlib import Path


def _build_pdf(pages: list[str]) -> bytes:
    """Build a minimal valid PDF with one text item per page."""
    buf = io.BytesIO()
    offsets: dict[int, int] = {}

    def w(data: str | bytes) -> None:
        if isinstance(data, str):
            data = data.encode("latin-1")
        buf.write(data)

    # Header
    w(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

    n = len(pages)
    # Object numbering: 1=Catalog, 2=Pages, then pairs (page, content) from 3 onward.
    page_objs = [3 + 2 * i for i in range(n)]
    content_objs = [4 + 2 * i for i in range(n)]

    # Object 1: Catalog
    offsets[1] = buf.tell()
    w("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")

    # Object 2: Pages
    offsets[2] = buf.tell()
    kids = " ".join(f"{o} 0 R" for o in page_objs)
    w(f"2 0 obj\n<< /Type /Pages /Kids [{kids}] /Count {n} >>\nendobj\n")

    for i, text in enumerate(pages):
        page_obj = page_objs[i]
        content_obj = content_objs[i]
        escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream = f"BT\n/F1 12 Tf\n72 {720 - i * 24} Td\n({escaped}) Tj\nET\n"
        stream_bytes = stream.encode("latin-1")

        # Page object
        offsets[page_obj] = buf.tell()
        w(f"{page_obj} 0 obj\n")
        w("<< /Type /Page\n")
        w("   /Parent 2 0 R\n")
        w("   /MediaBox [0 0 612 792]\n")
        w("   /Resources << /Font << /F1 << /Type /Font /Subtype /Type1")
        w(" /BaseFont /Helvetica >> >> >>\n")
        w(f"   /Contents {content_obj} 0 R\n")
        w(">>\nendobj\n")

        # Content stream
        offsets[content_obj] = buf.tell()
        w(f"{content_obj} 0 obj\n<< /Length {len(stream_bytes)} >>\nstream\n")
        buf.write(stream_bytes)
        w("\nendstream\nendobj\n")

    # Cross-reference table
    xref_pos = buf.tell()
    total = 2 + 2 * n
    w(f"xref\n0 {total + 1}\n")
    w("0000000000 65535 f \n")
    for obj_num in range(1, total + 1):
        w(f"{offsets[obj_num]:010d} 00000 n \n")

    # Trailer
    w(f"trailer\n<< /Size {total + 1} /Root 1 0 R >>\n")
    w(f"startxref\n{xref_pos}\n%%EOF\n")

    return buf.getvalue()


def main() -> None:
    out = Path(__file__).parent

    (out / "single_page.pdf").write_bytes(
        _build_pdf(["Statement Date: March 31 2026  Account: XXXX-1234  Balance: $1234.56"])
    )
    print("Created single_page.pdf")

    (out / "multi_page.pdf").write_bytes(
        _build_pdf(
            [
                "Page 1 - Account Summary  Opening Balance: $0.00  Closing Balance: $1234.56",
                "Page 2 - Transactions  03/01 Coffee Shop $4.50  03/02 Grocery Store $82.10",
            ]
        )
    )
    print("Created multi_page.pdf")


if __name__ == "__main__":
    main()
