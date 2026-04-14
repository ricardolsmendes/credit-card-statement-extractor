"""Generate statement PDF fixtures for transaction extractor tests.

Run once from the project root:
    python tests/fixtures/statements/create_fixtures.py

Fixtures generated:
    en_statement.pdf       — English headers, 4 transactions
    ptbr_statement.pdf     — pt-BR headers, same 4 transactions
    no_transactions_statement.pdf — valid PDF, no transaction header row
    partial_statement.pdf  — 2 parseable lines + 2 malformed lines
    ptbr_long_date_statement.pdf           — pt-BR long dates, no Beneficiário column
    ptbr_long_date_beneficiary_statement.pdf — pt-BR long dates, with Beneficiário column

Layout strategy
---------------
Each line is a single PDF text object rendered at a fixed y-coordinate.
The text strings embed the column spacing directly (≥2 spaces between
description and amount) so pdfplumber's extract_text() returns lines
with the spacing intact.  y-coordinates decrease top-to-bottom; we start
at y=700 and subtract 14 per line so pdfplumber returns them in source order.
"""

import io
from pathlib import Path


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_pdf(pages: list[list[str]]) -> bytes:
    """Build a minimal valid multi-page PDF.

    Each page is a list of pre-formatted text lines.  Lines are placed at
    x=50, decreasing y starting at 700 (14pt steps), so pdfplumber returns
    them top-to-bottom in source order.
    """
    buf = io.BytesIO()
    offsets: dict[int, int] = {}

    def w(data: str | bytes) -> None:
        if isinstance(data, str):
            data = data.encode("latin-1")
        buf.write(data)

    w(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

    n = len(pages)
    page_objs = [3 + 2 * i for i in range(n)]
    content_objs = [4 + 2 * i for i in range(n)]

    offsets[1] = buf.tell()
    w("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")

    offsets[2] = buf.tell()
    kids = " ".join(f"{o} 0 R" for o in page_objs)
    w(f"2 0 obj\n<< /Type /Pages /Kids [{kids}] /Count {n} >>\nendobj\n")

    for i, lines in enumerate(pages):
        page_obj = page_objs[i]
        content_obj = content_objs[i]

        stream_parts: list[str] = []
        y = 700
        for line in lines:
            if line:
                stream_parts.append(f"BT /F1 10 Tf 50 {y} Td ({_escape(line)}) Tj ET\n")
            y -= 14

        stream = "".join(stream_parts)
        stream_bytes = stream.encode("latin-1")

        offsets[page_obj] = buf.tell()
        w(f"{page_obj} 0 obj\n")
        w("<< /Type /Page\n")
        w("   /Parent 2 0 R\n")
        w("   /MediaBox [0 0 612 792]\n")
        w("   /Resources << /Font << /F1 << /Type /Font /Subtype /Type1")
        w(" /BaseFont /Courier >> >> >>\n")
        w(f"   /Contents {content_obj} 0 R\n")
        w(">>\nendobj\n")

        offsets[content_obj] = buf.tell()
        w(f"{content_obj} 0 obj\n<< /Length {len(stream_bytes)} >>\nstream\n")
        buf.write(stream_bytes)
        w("\nendstream\nendobj\n")

    xref_pos = buf.tell()
    total = 2 + 2 * n
    w(f"xref\n0 {total + 1}\n")
    w("0000000000 65535 f \n")
    for obj_num in range(1, total + 1):
        w(f"{offsets[obj_num]:010d} 00000 n \n")

    w(f"trailer\n<< /Size {total + 1} /Root 1 0 R >>\n")
    w(f"startxref\n{xref_pos}\n%%EOF\n")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Statement content
# ---------------------------------------------------------------------------
# 4 known transactions shared across en and pt-BR fixtures:
#   2026-03-01 / 01/03/2026   Coffee Shop           -4.50 / -4,50
#   2026-03-02 / 02/03/2026   Grocery Store         -82.10 / -82,10
#   2026-03-10 / 10/03/2026   Payment received      +500.00 / +500,00
#   2026-03-15 / 15/03/2026   Gas Station           -89.50 / -89,50
#
# Each transaction line uses at least 2 spaces before the amount field so the
# parser regex `\s{2,}` matches.  Column widths are fixed:
#   date:        10 chars   (padded to 12 with trailing spaces)
#   description: 28 chars   (left-aligned, padded)
#   amount:      right of description (≥2 spaces gap)
# ---------------------------------------------------------------------------

EN_HEADER = "Date        Description                    Amount"
EN_TXNS = [
    "2026-03-01  Coffee Shop                            -4.50",
    "2026-03-02  Grocery Store                         -82.10",
    "2026-03-10  Payment received                     +500.00",
    "2026-03-15  Gas Station                           -89.50",
]

PTBR_HEADER = "Data        Descricao                      Valor"
PTBR_TXNS = [
    "01/03/2026  Coffee Shop                            -4,50",
    "02/03/2026  Supermercado ABC                      -82,10",
    "10/03/2026  Pagamento recebido                   +500,00",
    "15/03/2026  Posto de Gasolina                     -89,50",
]

# Phase 7 fixture: long pt-BR dates, no Beneficiário column
# Header uses "Movimentacao" (ASCII alias for "Movimentação", a recognised description variant)
# Amounts use plain pt-BR numeric format (no currency prefix) so _TXN_RE can capture them.
PTBR_LONG_DATE_HEADER = "Data        Movimentacao                   Valor"
PTBR_LONG_DATE_TXNS = [
    "14 de mar. 2026  DrinksEBar                        -85,91",
    "14 de mar. 2026  Posto de Gasolina                 -169,66",
]

# Phase 8 fixture: long pt-BR dates, WITH Beneficiario column
# Four-column layout: Data / Movimentacao / Beneficiario / Valor
# "Beneficiario" is the ASCII alias for "Beneficiário" recognised by the parser.
# Beneficiary values are single tokens (no spaces) to survive pdfplumber's
# whitespace collapsing during text extraction.
PTBR_BENEFICIARY_HEADER = "Data              Movimentacao    Beneficiario             Valor"
PTBR_BENEFICIARY_TXNS = [
    "14 de mar. 2026  DrinksEBar      DrinksEBar               -85,91",
    "14 de mar. 2026  ABASTEC*Posto   PostoDeGasolina           -169,66",
]


def main() -> None:
    out = Path(__file__).parent

    # en_statement.pdf
    (out / "en_statement.pdf").write_bytes(
        _build_pdf(
            [
                [
                    "ACCOUNT SUMMARY",
                    "Account: XXXX-1234",
                    "Total: -176.10",
                    "",
                    EN_HEADER,
                    *EN_TXNS,
                ]
            ]
        )
    )
    print("Created en_statement.pdf")

    # ptbr_statement.pdf
    # "Descricao" is the ASCII alias for "Descrição" recognised by the parser.
    (out / "ptbr_statement.pdf").write_bytes(
        _build_pdf(
            [
                [
                    "RESUMO DA CONTA",
                    "Conta: XXXX-1234",
                    "Total: -176,10",
                    "",
                    PTBR_HEADER,
                    *PTBR_TXNS,
                ]
            ]
        )
    )
    print("Created ptbr_statement.pdf")

    # no_transactions_statement.pdf
    (out / "no_transactions_statement.pdf").write_bytes(
        _build_pdf(
            [
                [
                    "ACCOUNT SUMMARY",
                    "Account: XXXX-5678",
                    "Statement Date: 2026-03-31",
                    "Opening Balance: 0.00",
                    "Closing Balance: 0.00",
                    "No transactions this period.",
                ]
            ]
        )
    )
    print("Created no_transactions_statement.pdf")

    # partial_statement.pdf — 2 parseable + 2 malformed lines after the header
    # Note: no "Total" line after the header to keep the skipped count exact.
    (out / "partial_statement.pdf").write_bytes(
        _build_pdf(
            [
                [
                    "ACCOUNT SUMMARY",
                    "Account: XXXX-9999",
                    "Total: -86.60",
                    "",
                    EN_HEADER,
                    EN_TXNS[0],  # parseable
                    EN_TXNS[1],  # parseable
                    "NOT A DATE - Missing amount field",  # malformed: no date pattern
                    "Also no date or amount here",  # malformed: no date or amount
                ]
            ]
        )
    )
    print("Created partial_statement.pdf")

    # ptbr_long_date_statement.pdf — Phase 7: long pt-BR dates, no Beneficiário column
    (out / "ptbr_long_date_statement.pdf").write_bytes(
        _build_pdf(
            [
                [
                    "RESUMO DA CONTA",
                    "Conta: XXXX-2026",
                    "",
                    PTBR_LONG_DATE_HEADER,
                    *PTBR_LONG_DATE_TXNS,
                ]
            ]
        )
    )
    print("Created ptbr_long_date_statement.pdf")

    # ptbr_long_date_beneficiary_statement.pdf — Phase 8: long dates + Beneficiário column
    (out / "ptbr_long_date_beneficiary_statement.pdf").write_bytes(
        _build_pdf(
            [
                [
                    "RESUMO DA CONTA",
                    "Conta: XXXX-2026",
                    "",
                    PTBR_BENEFICIARY_HEADER,
                    *PTBR_BENEFICIARY_TXNS,
                ]
            ]
        )
    )
    print("Created ptbr_long_date_beneficiary_statement.pdf")


if __name__ == "__main__":
    main()
